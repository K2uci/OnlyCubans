from django import forms
from django.core.exceptions import ValidationError
from .models import Category, Tag, Post, Media, Comment, Report

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'is_nsfw']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Etiquetas separadas por comas'
        }),
        help_text="Separar etiquetas con comas"
    )
    
    scheduled_for = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    class Meta:
        model = Post
        fields = [
            'title', 'description', 'post_type', 'category', 
            'price', 'is_exclusive', 'allow_comments', 
            'allow_likes', 'allow_sharing', 'scheduled_for'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'post_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_exclusive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_likes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_sharing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        post_type = self.cleaned_data.get('post_type')
        
        if post_type == 'premium' and price <= 0:
            raise ValidationError("El contenido premium debe tener un precio mayor a 0.")
        
        return price

    def clean_scheduled_for(self):
        scheduled_for = self.cleaned_data.get('scheduled_for')
        if scheduled_for:
            from django.utils import timezone
            if scheduled_for <= timezone.now():
                raise ValidationError("La fecha programada debe ser en el futuro.")
        return scheduled_for

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['file', 'media_type', 'thumbnail', 'order', 'is_preview', 'is_downloadable']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'media_type': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_downloadable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe tu comentario...'
            }),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el motivo del reporte...'
            }),
        }

class PostSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar contenido...'
        })
    )
    
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tags = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Tag.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    post_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + list(Post.POST_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_range = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Cualquier fecha'),
            ('today', 'Hoy'),
            ('week', 'Esta semana'),
            ('month', 'Este mes'),
            ('year', 'Este año'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )