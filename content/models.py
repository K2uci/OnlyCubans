from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os

# Función para rutas únicas de archivos multimedia
def content_media_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('content_media', filename)

def thumbnail_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('thumbnails', filename)

class Category(models.Model):
    """
    Categorías para organizar el contenido
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_nsfw = models.BooleanField(default=True, help_text="Contenido para adultos")
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories'
    )
    
    # Métricas
    content_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    Etiquetas para contenido
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Post(models.Model):
    """
    Modelo principal para publicaciones de contenido
    """
    POST_TYPE_CHOICES = (
        ('public', 'Público'),
        ('premium', 'Premium'),
        ('private', 'Privado'),
        ('archived', 'Archivado'),
    )
    
    POST_STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('scheduled', 'Programado'),
        ('hidden', 'Oculto'),
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, blank=True)
    
    # Tipo y estado
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='public')
    status = models.CharField(max_length=10, choices=POST_STATUS_CHOICES, default='draft')
    
    # Categorización
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    # Precio para contenido premium
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00)]
    )
    
    # Configuración de visibilidad
    is_exclusive = models.BooleanField(
        default=False,
        help_text="Solo disponible para suscriptores premium"
    )
    allow_comments = models.BooleanField(default=True)
    allow_likes = models.BooleanField(default=True)
    allow_sharing = models.BooleanField(default=True)
    
    # Métricas
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Tiempo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'status']),
            models.Index(fields=['post_type', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.author.username}"
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def is_premium(self):
        return self.post_type == 'premium'

class Media(models.Model):
    """
    Archivos multimedia asociados a publicaciones
    """
    MEDIA_TYPE_CHOICES = (
        ('image', 'Imagen'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Documento'),
    )
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media_files'
    )
    
    file = models.FileField(upload_to=content_media_path)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    thumbnail = models.ImageField(upload_to=thumbnail_path, blank=True, null=True)
    
    # Metadata del archivo
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)  # en bytes
    duration = models.DurationField(null=True, blank=True)  # para video/audio
    resolution = models.CharField(max_length=20, blank=True)  # para video/imagen
    
    # Orden y visibilidad
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(
        default=False,
        help_text="Mostrar como vista previa gratuita"
    )
    
    # Protección de contenido
    watermark = models.BooleanField(default=True)
    is_downloadable = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = "Media"
    
    def __str__(self):
        return f"{self.media_type} - {self.post.title}"

class Comment(models.Model):
    """
    Comentarios en publicaciones
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    content = models.TextField(max_length=1000)
    is_edited = models.BooleanField(default=False)
    
    # Moderación
    is_approved = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    flagged_reason = models.CharField(max_length=200, blank=True)
    
    # Métricas
    likes_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'is_approved']),
        ]
    
    def __str__(self):
        return f"Comentario de {self.author.username} en {self.post.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None

class Like(models.Model):
    """
    Likes/Reacciones a publicaciones y comentarios
    """
    LIKE_TYPE_CHOICES = (
        ('like', 'Me gusta'),
        ('love', 'Me encanta'),
        ('fire', 'Caliente'),
        ('funny', 'Divertido'),
        ('wow', 'Sorprendido'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    
    # Puede ser like a post o comentario
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        null=True,
        blank=True
    )
    
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes',
        null=True,
        blank=True
    )
    
    like_type = models.CharField(max_length=10, choices=LIKE_TYPE_CHOICES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ('user', 'post'),
            ('user', 'comment')
        ]
        indexes = [
            models.Index(fields=['user', 'post']),
            models.Index(fields=['user', 'comment']),
        ]
    
    def __str__(self):
        if self.post:
            return f"{self.user.username} likes {self.post.title}"
        return f"{self.user.username} likes comment #{self.comment.id}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.post and not self.comment:
            raise ValidationError("Debe especificar un post o comentario")
        if self.post and self.comment:
            raise ValidationError("No puede tener ambos post y comentario")

class Bookmark(models.Model):
    """
    Guardar publicaciones para ver después
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='bookmarked_by'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} guardó {self.post.title}"

class View(models.Model):
    """
    Registro de visualizaciones de contenido
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='views'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='viewed_posts',
        null=True,
        blank=True
    )
    
    # Para usuarios no autenticados
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Información de la visualización
    view_duration = models.DurationField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    percentage_watched = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        viewer = self.user.username if self.user else f"Anónimo ({self.ip_address})"
        return f"Vista de {viewer} en {self.post.title}"

class Report(models.Model):
    """
    Reportes de contenido inapropiado
    """
    REPORT_REASON_CHOICES = (
        ('spam', 'Spam'),
        ('harassment', 'Acoso'),
        ('inappropriate', 'Contenido inapropiado'),
        ('copyright', 'Violación de copyright'),
        ('other', 'Otro'),
    )
    
    REPORT_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('reviewed', 'Revisado'),
        ('resolved', 'Resuelto'),
        ('dismissed', 'Desestimado'),
    )
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_made'
    )
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )
    
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )
    
    reason = models.CharField(max_length=20, choices=REPORT_REASON_CHOICES)
    description = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=10, choices=REPORT_STATUS_CHOICES, default='pending')
    
    # Moderación
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_reviewed'
    )
    review_notes = models.TextField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        target = f"Post: {self.post.title}" if self.post else f"Comment: #{self.comment.id}"
        return f"Reporte de {self.reporter.username} sobre {target}"