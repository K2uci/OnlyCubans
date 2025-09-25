from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from ..models import Post
from accounts.models import FollowerRelationship 
from django.shortcuts import get_object_or_404, redirect


@login_required
def home_feed(request):
    """Feed principal con contenido de usuarios seguidos"""
    user = request.user
    
    # Obtener usuarios seguidos
    following_ids = user.following_relationships.filter(
        is_active=True
    ).values_list('following_id', flat=True)
    
    # Posts de usuarios seguidos + posts públicos
    posts = Post.objects.filter(
        Q(author_id__in=following_ids) | Q(post_type='public'),
        status='published',
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related(
        'media_files', 'tags'
    ).order_by('-published_at')
    
    # Paginación
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'content/feed_home.html', {
        'page_obj': page_obj,
        'feed_type': 'home'
    })

@login_required
def discover_feed(request):
    """Feed de descubrimiento con contenido popular"""
    posts = Post.objects.filter(
        status='published',
        published_at__lte=timezone.now(),
        post_type='public'
    ).select_related('author', 'category').prefetch_related(
        'media_files', 'tags'
    ).annotate(
        engagement_score=models.Count('likes') + models.Count('comments') * 2
    ).order_by('-engagement_score', '-published_at')
    
    # Paginación
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'content/feed_discover.html', {
        'page_obj': page_obj,
        'feed_type': 'discover'
    })

@login_required
def creator_feed(request, username):
    """Feed específico de un creador"""
    from accounts.models import User
    creator = get_object_or_404(User, username=username, user_type='creator')
    
    # Verificar si el usuario tiene acceso al contenido premium
    has_access = False
    if request.user == creator:
        has_access = True
    else:
        # Verificar suscripción activa
        subscription = FollowerRelationship.objects.filter(
            follower=request.user,
            following=creator,
            is_paid_subscription=True,
            is_active=True
        ).first()
        
        if subscription and subscription.is_subscription_active:
            has_access = True
    
    posts = Post.objects.filter(
        author=creator,
        status='published',
        published_at__lte=timezone.now()
    )
    
    # Filtrar por acceso
    if has_access:
        posts = posts.filter(Q(post_type='public') | Q(post_type='premium'))
    else:
        posts = posts.filter(post_type='public')
    
    posts = posts.select_related('author', 'category').prefetch_related(
        'media_files', 'tags'
    ).order_by('-published_at')
    
    # Paginación
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'content/feed_creator.html', {
        'page_obj': page_obj,
        'creator': creator,
        'has_access': has_access,
        'feed_type': 'creator'
    })

@login_required
def category_feed(request, slug):
    """Feed por categoría"""
    from ..models import Category
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    posts = Post.objects.filter(
        category=category,
        status='published',
        published_at__lte=timezone.now(),
        post_type='public'
    ).select_related('author', 'category').prefetch_related(
        'media_files', 'tags'
    ).order_by('-published_at')
    
    # Paginación
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'content/feed_category.html', {
        'page_obj': page_obj,
        'category': category,
        'feed_type': 'category'
    })