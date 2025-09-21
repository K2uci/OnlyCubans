from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CreatorProfile, FollowerRelationship, BlockedUser, UserSettings

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_banned', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_banned', 'gender')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('user_type', 'phone_number', 'birth_date', 'gender', 
                      'bio', 'profile_picture', 'cover_photo', 'website',
                      'is_verified', 'is_banned', 'show_birthdate', 'show_gender',
                      'subscription_price', 'has_active_subscription_model')
        }),
    )

@admin.register(CreatorProfile)
class CreatorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'stage_name', 'category', 'total_earnings', 'total_subscribers')
    list_filter = ('category', 'id_verified', 'age_verified')
    search_fields = ('user__username', 'stage_name', 'category')

admin.site.register(FollowerRelationship)
admin.site.register(BlockedUser)
admin.site.register(UserSettings)