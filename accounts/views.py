# Create your views here.

from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    """
    Klasa obsługująca logowanie użytkownika.
    """
    template_name = 'login.html'  # Ścieżka do szablonu logowania
    redirect_authenticated_user = True  # Przekierowuje już zalogowanych użytkowników
    next_page = reverse_lazy('browse_processes')
