from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from ..models import Post, Comment, Like, Bookmark

@login_required
def like_post(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post = get_object_or_404(Post, pk=pk)
        like_type = request.POST.get('like_type', 'like')
        
        # Verificar si ya existe un like
        existing_like = Like.objects.filter(
            user=request.user, 
            post=post
        ).first()
        
        if existing_like:
            # Actualizar tipo de like
            existing_like.like_type = like_type
            existing_like.save()
            liked = True
        else:
            # Crear nuevo like
            Like.objects.create(
                user=request.user,
                post=post,
                like_type=like_type
            )
            liked = True
            post.likes_count += 1
            post.save(update_fields=['likes_count'])
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': post.likes.count(),
            'like_type': like_type
        })
    
    return JsonResponse({'success': False}, status=400)

@login_required
def unlike_post(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post = get_object_or_404(Post, pk=pk)
        
        try:
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            post.likes_count = max(0, post.likes_count - 1)
            post.save(update_fields=['likes_count'])
            
            return JsonResponse({
                'success': True,
                'liked': False,
                'likes_count': post.likes.count()
            })
        except Like.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Like no encontrado'})
    
    return JsonResponse({'success': False}, status=400)

@login_required
def add_comment(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=pk)
        
        if not post.allow_comments:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Los comentarios están deshabilitados para esta publicación'
                })
            messages.error(request, 'Los comentarios están deshabilitados para esta publicación.')
            return redirect('content:post_detail', pk=post.pk)
        
        parent_id = request.POST.get('parent_id')
        content = request.POST.get('content', '').strip()
        
        if not content:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'El comentario no puede estar vacío'
                })
            messages.error(request, 'El comentario no puede estar vacío.')
            return redirect('content:post_detail', pk=post.pk)
        
        parent_comment = None
        if parent_id:
            try:
                parent_comment = Comment.objects.get(pk=parent_id, post=post)
            except Comment.DoesNotExist:
                pass
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            parent=parent_comment,
            content=content
        )
        
        # Actualizar contador de comentarios
        post.comments_count = post.comments.count()
        post.save(update_fields=['comments_count'])
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'author_name': comment.author.username,
                'author_avatar': comment.author.profile_picture.url if comment.author.profile_picture else '',
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
                'is_reply': comment.is_reply
            })
        
        messages.success(request, 'Comentario agregado exitosamente.')
        return redirect('content:post_detail', pk=post.pk)
    
    return JsonResponse({'success': False}, status=400)

@login_required
def delete_comment(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=pk)
        
        # Verificar permisos (autor del comentario o autor del post)
        if comment.author != request.user and comment.post.author != request.user:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes permisos para eliminar este comentario'
                })
            messages.error(request, 'No tienes permisos para eliminar este comentario.')
            return redirect('content:post_detail', pk=comment.post.pk)
        
        post = comment.post
        comment.delete()
        
        # Actualizar contador de comentarios
        post.comments_count = post.comments.count()
        post.save(update_fields=['comments_count'])
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, 'Comentario eliminado exitosamente.')
        return redirect('content:post_detail', pk=post.pk)
    
    return JsonResponse({'success': False}, status=400)

@login_required
def bookmark_post(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        post = get_object_or_404(Post, pk=pk)
        
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            post=post
        )
        
        if not created:
            bookmark.delete()
            bookmarked = False
        else:
            bookmarked = True
        
        return JsonResponse({
            'success': True,
            'bookmarked': bookmarked
        })
    
    return JsonResponse({'success': False}, status=400)

@login_required
def like_comment(request, pk):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        comment = get_object_or_404(Comment, pk=pk)
        
        existing_like = Like.objects.filter(
            user=request.user, 
            comment=comment
        ).first()
        
        if existing_like:
            existing_like.delete()
            liked = False
            comment.likes_count = max(0, comment.likes_count - 1)
        else:
            Like.objects.create(
                user=request.user,
                comment=comment
            )
            liked = True
            comment.likes_count += 1
        
        comment.save(update_fields=['likes_count'])
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': comment.likes_count
        })
    
    return JsonResponse({'success': False}, status=400)