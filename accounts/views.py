from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView as BaseLoginView
from .forms import CustomUserCreationForm  # Importa el formulario personalizado
from .models import User, CreatorProfile  # Importa los modelos

@method_decorator(csrf_protect, name='dispatch')
class CustomLoginView(BaseLoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            if user.is_active and not user.is_banned:
                login(self.request, user)
                messages.success(self.request, f'¡Bienvenido de nuevo, {user.username}!')
                
                if user.is_creator:
                    return redirect('creator:dashboard')
                else:
                    return redirect('home')
            else:
                if user.is_banned:
                    messages.error(self.request, 'Tu cuenta ha sido suspendida. Contacta al soporte.')
                else:
                    messages.error(self.request, 'Tu cuenta está inactiva.')
                return self.form_invalid(form)
        else:
            messages.error(self.request, 'Usuario o contraseña incorrectos.')
            return self.form_invalid(form)
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        
        if self.request.user.is_creator:
            return reverse_lazy('creator:dashboard')
        return reverse_lazy('home')

@csrf_protect
def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                
                # Asignar campos adicionales
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.user_type = form.cleaned_data['user_type']
                
                user.save()
                
                # Crear perfil de creador si es necesario
                if user.user_type == 'creator':
                    CreatorProfile.objects.create(
                        user=user,
                        stage_name=f"{user.first_name} {user.last_name}".strip()
                    )
                
                # Iniciar sesión automáticamente
                login(request, user)
                
                messages.success(
                    request, 
                    f'¡Cuenta creada exitosamente! Bienvenido a OnlyCubans, {user.username}.'
                )
                
                # Redirigir según el tipo de usuario
                if user.is_creator:
                    return redirect('creator:onboarding')  # O la página que prefieras
                else:
                    return redirect('home')
                    
            except Exception as e:
                messages.error(
                    request, 
                    f'Error al crear la cuenta: {str(e)}. Por favor, intenta nuevamente.'
                )
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def logout_confirmation(request):
    return render(request, 'accounts/logout_confirmation.html')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def settings(request):
    return render(request, 'accounts/settings.html', {'user': request.user})

# Vista alternativa de login basada en función
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active and not user.is_banned:
                    login(request, user)
                    messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
                    
                    if user.is_creator:
                        return redirect('creator:dashboard')
                    else:
                        next_url = request.GET.get('next')
                        if next_url:
                            return redirect(next_url)
                        return redirect('home')
                else:
                    if user.is_banned:
                        messages.error(request, 'Tu cuenta ha sido suspendida. Contacta al soporte.')
                    else:
                        messages.error(request, 'Tu cuenta está inactiva.')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor, ingresa credenciales válidas.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'title': 'Iniciar Sesión - OnlyCubans'
    })