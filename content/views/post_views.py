from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models import Post, Media, Category, Tag, View
from ..forms import PostForm, MediaForm, PostSearchForm, CommentForm

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'content/posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Post.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags', 'media_files')
        
        # Filtrar por permisos de usuario
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
            
        # Para usuarios regulares, mostrar solo contenido público o premium al que tengan acceso
        if user.user_type == 'regular':
            # Aquí se implementará la lógica de suscripciones más adelante
            queryset = queryset.filter(
                Q(post_type='public') | 
                Q(author__in=user.following_relationships.filter(is_active=True).values('following'))
            )
        
        # Búsqueda y filtros
        form = PostSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            post_type = form.cleaned_data.get('post_type')
            date_range = form.cleaned_data.get('date_range')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(tags__name__icontains=query)
                ).distinct()
            
            if category:
                queryset = queryset.filter(category=category)
            
            if post_type:
                queryset = queryset.filter(post_type=post_type)
            
            if date_range:
                now = timezone.now()
                if date_range == 'today':
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    queryset = queryset.filter(created_at__gte=start_date)
                elif date_range == 'week':
                    start_date = now - timezone.timedelta(days=7)
                    queryset = queryset.filter(created_at__gte=start_date)
                elif date_range == 'month':
                    start_date = now - timezone.timedelta(days=30)
                    queryset = queryset.filter(created_at__gte=start_date)
                elif date_range == 'year':
                    start_date = now - timezone.timedelta(days=365)
                    queryset = queryset.filter(created_at__gte=start_date)
        
        return queryset.order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PostSearchForm(self.request.GET)
        context['categories'] = Category.objects.filter(is_active=True)
        return context

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'content/posts/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'author', 'category'
        ).prefetch_related(
            'media_files', 'comments__author', 'tags'
        )
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        post = self.object
        
        # Registrar vista
        if post.is_published:
            View.objects.create(
                post=post,
                user=request.user if request.user.is_authenticated else None,
                ip_address=self.get_client_ip(),
                session_key=request.session.session_key
            )
            
            # Actualizar contador de vistas
            post.views_count = post.views.count()
            post.save(update_fields=['views_count'])
        
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Verificar permisos de acceso
        user = self.request.user
        can_access = self.can_user_access_post(user, post)
        context['can_access'] = can_access
        
        if can_access:
            context['comment_form'] = CommentForm()
            context['related_posts'] = self.get_related_posts(post)
        
        return context
    
    def can_user_access_post(self, user, post):
        if post.status != 'published':
            return False
        
        if post.post_type == 'public':
            return True
        
        if post.post_type == 'premium':
            # Verificar si el usuario es el autor
            if user == post.author:
                return True
            
            # Verificar si el usuario está suscrito al creador
            # Esta lógica se completará cuando se implemente el módulo de suscripciones
            if hasattr(user, 'following_relationships'):
                subscription = user.following_relationships.filter(
                    following=post.author,
                    is_paid_subscription=True,
                    is_active=True
                ).first()
                
                if subscription and subscription.is_subscription_active:
                    return True
            
            return False
        
        return False
    
    def get_related_posts(self, post):
        return Post.objects.filter(
            category=post.category,
            status='published',
            published_at__lte=timezone.now()
        ).exclude(id=post.id).select_related('author')[:6]

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'content/posts/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.ip_address = self.get_client_ip()
        
        # Manejar el estado basado en la programación
        if form.instance.scheduled_for:
            form.instance.status = 'scheduled'
        else:
            form.instance.status = 'published'
            form.instance.published_at = timezone.now()
        
        response = super().form_valid(form)
        
        # Manejar etiquetas
        tags_input = form.cleaned_data.get('tags_input', '')
        if tags_input:
            self.handle_tags(form.instance, tags_input)
        
        messages.success(self.request, 'Publicación creada exitosamente.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_form'] = MediaForm()
        return context
    
    def handle_tags(self, post, tags_input):
        from ..models import Tag
        tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
        
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name.lower(),
                defaults={'is_active': True}
            )
            post.tags.add(tag)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'content/posts/post_form.html'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
    
    def form_valid(self, form):
        # Manejar etiquetas
        tags_input = form.cleaned_data.get('tags_input', '')
        if tags_input:
            self.handle_tags(form.instance, tags_input)
        
        messages.success(self.request, 'Publicación actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        post = self.get_object()
        initial['tags_input'] = ', '.join([tag.name for tag in post.tags.all()])
        return initial
    
    def handle_tags(self, post, tags_input):
        from ..models import Tag
        tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
        current_tags = set(post.tags.values_list('name', flat=True))
        new_tags = set(tag_names)
        
        # Remover tags que ya no están
        for tag_name in current_tags - new_tags:
            tag = Tag.objects.get(name=tag_name)
            post.tags.remove(tag)
        
        # Agregar nuevos tags
        for tag_name in new_tags - current_tags:
            tag, created = Tag.objects.get_or_create(
                name=tag_name.lower(),
                defaults={'is_active': True}
            )
            post.tags.add(tag)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_form'] = MediaForm()
        context['editing'] = True
        return context

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'content/posts/post_confirm_delete.html'
    success_url = reverse_lazy('content:post_list')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Publicación eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)

@login_required
def post_draft_list(request):
    drafts = Post.objects.filter(
        author=request.user,
        status='draft'
    ).order_by('-created_at')
    
    return render(request, 'content/post_draft_list.html', {
        'drafts': drafts
    })

@login_required
def publish_draft(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if post.status == 'draft':
        post.status = 'published'
        post.published_at = timezone.now()
        post.save()
        messages.success(request, 'Publicación publicada exitosamente.')
    
    return redirect('content:post_detail', pk=post.pk)