from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from ..models import Report, Post, Comment
from ..forms import ReportForm

@login_required
def report_content(request):
    """Reportar contenido inapropiado"""
    if request.method == 'POST':
        form = ReportForm(request.POST)
        
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            
            # Determinar si es post o comentario
            post_id = request.POST.get('post_id')
            comment_id = request.POST.get('comment_id')
            
            if post_id:
                report.post = get_object_or_404(Post, pk=post_id)
            elif comment_id:
                report.comment = get_object_or_404(Comment, pk=comment_id)
            
            report.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, 'Reporte enviado exitosamente. Revisaremos el contenido pronto.')
            return redirect(report.post.get_absolute_url() if report.post else report.comment.post.get_absolute_url())
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False}, status=400)

def is_moderator(user):
    return user.is_staff or user.is_superuser or user.user_type == 'admin'

@user_passes_test(is_moderator)
def moderation_dashboard(request):
    """Panel de moderación"""
    pending_reports = Report.objects.filter(status='pending').select_related(
        'reporter', 'post', 'comment'
    ).order_by('-created_at')
    
    # Estadísticas
    stats = {
        'pending_reports': pending_reports.count(),
        'total_reports': Report.objects.count(),
        'resolved_reports': Report.objects.filter(status='resolved').count(),
    }
    
    return render(request, 'content/moderation_dashboard.html', {
        'pending_reports': pending_reports[:10],
        'stats': stats
    })

@user_passes_test(is_moderator)
def report_list(request):
    """Lista de todos los reportes"""
    reports = Report.objects.all().select_related(
        'reporter', 'post', 'comment', 'reviewed_by'
    ).order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Paginación
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'content/report_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter
    })

@user_passes_test(is_moderator)
def review_report(request, pk):
    """Revisar un reporte específico"""
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        review_notes = request.POST.get('review_notes', '')
        
        if action == 'resolve':
            report.status = 'resolved'
            messages.success(request, 'Reporte marcado como resuelto.')
        elif action == 'dismiss':
            report.status = 'dismissed'
            messages.success(request, 'Reporte desestimado.')
        
        report.reviewed_by = request.user
        report.review_notes = review_notes
        report.reviewed_at = timezone.now()
        report.save()
        
        return redirect('content:moderation_dashboard')
    
    return render(request, 'content/review_report.html', {
        'report': report
    })

@user_passes_test(is_moderator)
def hide_content(request, pk):
    """Ocultar contenido reportado"""
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        
        if content_type == 'post':
            post = get_object_or_404(Post, pk=pk)
            post.status = 'hidden'
            post.save()
            messages.success(request, 'Publicación ocultada exitosamente.')
            return redirect('content:moderation_dashboard')
        
        elif content_type == 'comment':
            comment = get_object_or_404(Comment, pk=pk)
            comment.is_approved = False
            comment.save()
            messages.success(request, 'Comentario ocultado exitosamente.')
            return redirect('content:moderation_dashboard')
    
    return JsonResponse({'success': False}, status=400)