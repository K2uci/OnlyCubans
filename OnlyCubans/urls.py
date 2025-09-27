from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls') , name="accounts"),
    path('content/', include('content.urls'), name="content"),
    # path('subscriptions/', include('subscriptions.urls')),
    # path('messages/', include('messaging.urls')),
    # path('notifications/', include('notifications.urls')),
    # path('analytics/', include('analytics.urls')),
]

# Personalización del admin
admin.site.site_header = "Adult Social Network - Administración"
admin.site.site_title = "Adult Social Network"
admin.site.index_title = "Panel de Administración"