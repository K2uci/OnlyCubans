from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Importar todas las vistas modularizadas
from .views.post_views import *
from .views.media_views import *
from .views.interaction_views import *
from .views.feed_views import *
from .views.moderation_views import *

@login_required
def content_dashboard(request):
    """Dashboard principal de contenido"""
    user = request.user
    
    # Estadísticas para el dashboard
    if user.is_creator:
        user_posts = Post.objects.filter(author=user)
        stats = {
            'total_posts': user_posts.count(),
            'published_posts': user_posts.filter(status='published').count(),
            'draft_posts': user_posts.filter(status='draft').count(),
            'total_views': sum(post.views_count for post in user_posts),
            'total_likes': sum(post.likes_count for post in user_posts),
            'total_comments': sum(post.comments_count for post in user_posts),
        }
    else:
        stats = None
    
    # Posts recientes del usuario
    recent_posts = Post.objects.filter(author=user).order_by('-created_at')[:5]
    
    # Feed de actividad reciente (likes, comentarios en posts del usuario)
    recent_activity = {
        'new_likes': Like.objects.filter(post__author=user).select_related('user', 'post').order_by('-created_at')[:10],
        'new_comments': Comment.objects.filter(post__author=user).select_related('author', 'post').order_by('-created_at')[:10],
    }

    draft_count = user.posts.filter(status='draft').count()
    
    return render(request, 'content/dashboard/dashboard.html', {
        'stats': stats,
        'recent_posts': recent_posts,
        'recent_activity': recent_activity,
        'draft_count': draft_count,
    })