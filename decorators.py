from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from migrationsdb.models import User


def library_access_required(view_func):
    """
    Decorador que permite acceso a bibliotecas:
    - Administradores y Bibliotecarios pueden ver cualquier biblioteca
    - Lectores solo pueden ver su propia biblioteca
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, user_id, *args, **kwargs):
        # Obtener el usuario de la biblioteca
        library_user = get_object_or_404(User, id=user_id)

        # Verificar si el usuario tiene permisos globales
        if (request.user.has_perm('migrationsdb.view_all_libraries') or
                request.user.groups.filter(name__in=['Administradores', 'Bibliotecarios']).exists()):
            return view_func(request, user_id, *args, **kwargs)

        # Verificar si es su propia biblioteca
        if hasattr(request.user, 'user') and request.user.user == library_user:
            return view_func(request, user_id, *args, **kwargs)

        # Si no tiene permisos
        messages.error(request, 'No tienes permisos para acceder a esta biblioteca.')
        return redirect('home')

    return wrapper


def library_management_required(view_func):
    """
    Decorador para operaciones de gestión de biblioteca:
    - Solo Administradores y Bibliotecarios pueden gestionar bibliotecas
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, user_id, *args, **kwargs):
        # Verificar permisos de gestión
        if (request.user.has_perm('migrationsdb.manage_library') or
                request.user.groups.filter(name__in=['Administradores', 'Bibliotecarios']).exists()):
            return view_func(request, user_id, *args, **kwargs)

        messages.error(request, 'No tienes permisos para gestionar bibliotecas.')
        return redirect('home')

    return wrapper


def reports_required(view_func):
    """
    Decorador para generar reportes:
    - Solo usuarios con permiso generate_reports
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if (request.user.has_perm('migrationsdb.generate_reports') or
                request.user.groups.filter(name__in=['Administradores', 'Bibliotecarios']).exists()):
            return view_func(request, *args, **kwargs)

        messages.error(request, 'No tienes permisos para generar reportes.')
        return redirect('home')

    return wrapper


def import_books_required(view_func):
    """
    Decorador para importar libros desde fuentes externas:
    - Solo usuarios con permiso import_books
    """

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if (request.user.has_perm('migrationsdb.import_books') or
                request.user.groups.filter(name__in=['Administradores', 'Bibliotecarios']).exists()):
            return view_func(request, *args, **kwargs)

        messages.error(request, 'No tienes permisos para importar libros.')
        return redirect('home')

    return wrapper