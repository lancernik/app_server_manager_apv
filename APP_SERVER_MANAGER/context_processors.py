def active_menu(request):
    selected = ''
    resolver_match = request.resolver_match
    if resolver_match:
        view_func = resolver_match.func
        view_class = getattr(view_func, 'view_class', None)
        if view_class and hasattr(view_class, 'selected'):
            selected = view_class.selected
    return {'menu_selected': str(selected)}
