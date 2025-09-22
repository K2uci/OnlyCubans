from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls'))
    # path('content/', include('content.urls')),
    # path('subscriptions/', include('subscriptions.urls')),
    # path('messages/', include('messaging.urls')),
    # path('notifications/', include('notifications.urls')),
    # path('analytics/', include('analytics.urls')),
]
