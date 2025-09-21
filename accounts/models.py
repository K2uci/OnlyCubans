from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings
import uuid
import os

# Función para rutas únicas de archivos de perfil
def profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profile_images', filename)

def cover_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('cover_photos', filename)

class User(AbstractUser):
    # Tipos de usuario
    USER_TYPE_CHOICES = (
        ('regular', 'Usuario Regular'),
        ('creator', 'Creador de Contenido'),
        ('admin', 'Administrador'),
    )
    
    # Géneros
    GENDER_CHOICES = (
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
        ('prefer_not_to_say', 'Prefiero no decir'),
    )
    
    # Campos adicionales
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='regular')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número de teléfono debe tener el formato: '+999999999'. Hasta 15 dígitos."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to=profile_image_path, blank=True)
    cover_photo = models.ImageField(upload_to=cover_image_path, blank=True)
    website = models.URLField(max_length=200, blank=True)
    
    # Verificación y estado
    is_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    
    # Configuración de privacidad
    show_birthdate = models.BooleanField(default=False)
    show_gender = models.BooleanField(default=False)
    
    # Métricas
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    
    # Campos de tiempo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Configuración de suscripciones
    subscription_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Precio mensual de suscripción para creadores"
    )
    has_active_subscription_model = models.BooleanField(
        default=False,
        help_text="Indica si el creador acepta suscriptores pagados"
    )
    
    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"
    
    @property
    def is_creator(self):
        return self.user_type == 'creator'
    
    @property
    def age(self):
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

class CreatorProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='creator_profile'
    )
    
    # Información profesional
    stage_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Etiquetas separadas por comas")
    
    # Detalles del creador
    about = models.TextField(max_length=1000, blank=True)
    content_preview = models.TextField(
        max_length=500, 
        blank=True, 
        help_text="Breve descripción del contenido que ofrece"
    )
    
    # Estadísticas del creador
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_subscribers = models.PositiveIntegerField(default=0)
    content_count = models.PositiveIntegerField(default=0)
    
    # Configuración de contenido
    welcome_message = models.TextField(
        max_length=500, 
        blank=True, 
        help_text="Mensaje de bienvenida para nuevos suscriptores"
    )
    
    # Configuración de pagos
    payout_method = models.CharField(
        max_length=20,
        choices=(
            ('bank_transfer', 'Transferencia Bancaria'),
            ('paypal', 'PayPal'),
            ('crypto', 'Criptomoneda'),
        ),
        blank=True
    )
    payout_email = models.EmailField(blank=True)
    
    # Verificación
    id_verified = models.BooleanField(default=False)
    age_verified = models.BooleanField(default=False)
    
    # Términos y condiciones
    accepts_terms = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de Creador: {self.user.username}"

class FollowerRelationship(models.Model):
    follower = models.ForeignKey(
        User, 
        related_name='following_relationships',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User, 
        related_name='follower_relationships',
        on_delete=models.CASCADE
    )
    
    # Para relaciones con creadores (suscripciones pagadas)
    is_paid_subscription = models.BooleanField(default=False)
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    subscription_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Estado de la relación
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
            models.Index(fields=['following', 'follower']),
        ]
    
    def __str__(self):
        return f"{self.follower} sigue a {self.following}"
    
    @property
    def is_subscription_active(self):
        if self.is_paid_subscription and self.subscription_end:
            return timezone.now() < self.subscription_end
        return False

class BlockedUser(models.Model):
    blocker = models.ForeignKey(
        User, 
        related_name='blocked_users',
        on_delete=models.CASCADE
    )
    blocked = models.ForeignKey(
        User, 
        related_name='blocked_by',
        on_delete=models.CASCADE
    )
    
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('blocker', 'blocked')
    
    def __str__(self):
        return f"{self.blocker} bloqueó a {self.blocked}"

class UserSettings(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='settings'
    )
    
    # Configuración de notificaciones
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Notificaciones específicas
    notify_new_follower = models.BooleanField(default=True)
    notify_new_message = models.BooleanField(default=True)
    notify_likes = models.BooleanField(default=True)
    notify_comments = models.BooleanField(default=True)
    notify_mentions = models.BooleanField(default=True)
    
    # Privacidad
    profile_private = models.BooleanField(default=False)
    show_online_status = models.BooleanField(default=True)
    allow_messages_from = models.CharField(
        max_length=20,
        choices=(
            ('everyone', 'Todos'),
            ('followed', 'Solo seguidores'),
            ('none', 'Nadie'),
        ),
        default='everyone'
    )
    
    # Contenido sensible
    show_sensitive_content = models.BooleanField(default=False)
    
    # Idioma y región
    language = models.CharField(max_length=10, default='es')
    timezone = models.CharField(max_length=50, default='UTC')
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Configuración de {self.user.username}"