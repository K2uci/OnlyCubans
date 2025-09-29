from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def home_redirect(request):
    """
    Vista principal que redirige según el estado de autenticación
    """
    if request.user.is_authenticated:
        return redirect('content:dashboard')  # Redirige al dashboard si está logueado
    else:
        return redirect('login')  # Redirige al login si no está logueado