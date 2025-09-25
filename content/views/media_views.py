from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from ..models import Media, Post
from ..forms import MediaForm

class MediaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Media
    form_class = MediaForm
    
    def test_func(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        return self.request.user == post.author
    
    def form_valid(self, form):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        form.instance.post = post
        
        # Procesar archivo
        media_file = form.cleaned_data['file']
        form.instance.file_name = media_file.name
        form.instance.file_size = media_file.size
        
        response = super().form_valid(form)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'media_id': self.object.id,
                'file_url': self.object.file.url,
                'media_type': self.object.media_type
            })
        
        messages.success(self.request, 'Archivo multimedia agregado exitosamente.')
        return response
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('content:post_edit', kwargs={'pk': self.kwargs.get('post_id')})

class MediaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Media
    form_class = MediaForm
    
    def test_func(self):
        media = self.get_object()
        return self.request.user == media.post.author
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'media_id': self.object.id
            })
        
        messages.success(self.request, 'Archivo multimedia actualizado exitosamente.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('content:post_edit', kwargs={'pk': self.object.post.pk})

class MediaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Media
    
    def test_func(self):
        media = self.get_object()
        return self.request.user == media.post.author
    
    def delete(self, request, *args, **kwargs):
        media = self.get_object()
        post_id = media.post.pk
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            media.delete()
            return JsonResponse({'success': True})
        
        media.delete()
        messages.success(request, 'Archivo multimedia eliminado exitosamente.')
        return redirect('content:post_edit', pk=post_id)

@login_required
def update_media_order(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        media_order = request.POST.getlist('media_order[]')
        
        for index, media_id in enumerate(media_order):
            try:
                media = Media.objects.get(id=media_id, post__author=request.user)
                media.order = index
                media.save()
            except Media.DoesNotExist:
                continue
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)