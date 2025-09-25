from django.urls import path, include
from . import views
from .views_main import content_dashboard

app_name = 'content'

urlpatterns = [
    # Dashboard y feeds
    path('', content_dashboard, name='dashboard'),
    path('feed/', views.home_feed, name='home_feed'),
    path('discover/', views.discover_feed, name='discover_feed'),
    path('feed/<str:username>/', views.creator_feed, name='creator_feed'),
    path('category/<slug:slug>/', views.category_feed, name='category_feed'),
    
    # Posts
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/create/', views.PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('posts/drafts/', views.post_draft_list, name='post_draft_list'),
    path('posts/<int:pk>/publish/', views.publish_draft, name='publish_draft'),
    
    # Interacciones
    path('posts/<int:pk>/like/', views.like_post, name='like_post'),
    path('posts/<int:pk>/unlike/', views.unlike_post, name='unlike_post'),
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('comments/<int:pk>/like/', views.like_comment, name='like_comment'),
    path('posts/<int:pk>/bookmark/', views.bookmark_post, name='bookmark_post'),
    
    # Media
    path('posts/<int:post_id>/media/add/', views.MediaCreateView.as_view(), name='media_add'),
    path('media/<int:pk>/edit/', views.MediaUpdateView.as_view(), name='media_edit'),
    path('media/<int:pk>/delete/', views.MediaDeleteView.as_view(), name='media_delete'),
    path('media/order/', views.update_media_order, name='update_media_order'),
    
    # Moderación
    path('report/', views.report_content, name='report_content'),
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderation/reports/', views.report_list, name='report_list'),
    path('moderation/reports/<int:pk>/review/', views.review_report, name='review_report'),
    path('moderation/hide/<int:pk>/', views.hide_content, name='hide_content'),
]