import re

from django.conf import settings
from django.shortcuts import redirect

LOGIN_URL = '/accounts/login/'

LOGIN_EXEMPT_URLS = [
    r'^accounts/login/$',  # Strona logowania
]


class LoginRequiredMiddleware:
    """
    Middleware wymuszające logowanie na wszystkich stronach,
    z wyjątkiem adresów URL zdefiniowanych w ustawieniach.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        exempt_urls = [re.compile(settings.LOGIN_URL.lstrip('/'))]
        if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
            exempt_urls += [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]
        self.exempt_urls = exempt_urls

    def __call__(self, request):
        # Jeśli użytkownik nie jest zalogowany
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            # Sprawdzamy, czy ścieżka nie znajduje się na liście wyjątków
            if not any(m.match(path) for m in self.exempt_urls):
                return redirect(settings.LOGIN_URL)
        return self.get_response(request)
