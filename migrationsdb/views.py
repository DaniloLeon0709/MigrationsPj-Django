from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.utils import json

from decorators import library_management_required, library_access_required
from migrationsdb.forms import UserForm, AuthorForm, GenreForm, BookForm
from migrationsdb.models import User, Author, Genre, Book
from migrationsdb.serializers import GenreSerializer
from migrationsdb.services import pdf_services

from django.db import transaction
from datetime import date

from migrationsdb.services.openlibrary_service import search_books as ol_search, get_book_by_isbn as ol_get_by_isbn

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser, Group, Permission


@login_required
def home(request):
    """
    Muestra la página principal con la lista de todos los usuarios ordenados por fecha de creación.
    """
    users = User.objects.select_related('auth_user').prefetch_related('auth_user__groups').all().order_by('last_name', 'first_name')

    # Contexto adicional para administradores
    auth_count = users.filter(auth_user__isnull=False).count()
    context = {
        'users': users,
        'auth_count': auth_count,
        'is_admin': request.user.is_superuser or request.user.groups.filter(name='Administradores').exists(),
        'is_librarian': request.user.groups.filter(name__in=['Administradores', 'Bibliotecarios']).exists(),
    }

    return render(request, 'migrationsdb/home.html', context)

@login_required
@permission_required('migrationsdb.add_user', raise_exception=True)
def create_user(request):
    """
    Maneja la creación de un nuevo usuario. Muestra el formulario en GET y procesa los datos en POST.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el formulario de usuario o redirección al home tras creación exitosa.
    """
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()  # Guardar y obtener la instancia del usuario creado

            # Crear usuario de autenticación si se solicita
            if form.cleaned_data.get('create_auth_user'):
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')

                try:
                    auth_user = user.create_auth_user(username, password)

                    # Asignar al grupo 'Lectores' por defecto
                    lectores_group, _ = Group.objects.get_or_create(name='Lectores')
                    auth_user.groups.add(lectores_group)

                    messages.success(request, f'Usuario {user.first_name} creado exitosamente con acceso al sistema.')
                except Exception as e:
                    messages.warning(request, f'Usuario creado pero error al crear acceso al sistema: {e}')
            else:
                messages.success(request, f'Usuario {user.first_name} creado exitosamente (solo biblioteca).')

            return redirect('home')
    else:
        form = UserForm()
    return render(request, 'migrationsdb/user_form.html', {'form': form})

@login_required
@permission_required('migrationsdb.change_user', raise_exception=True)
def update_user(request, user_id):
    """
    Maneja la actualización de un usuario existente. Busca el usuario por ID y permite editarlo.
    :param request: El objeto HttpRequest de Django.
    :param user_id: ID del usuario a actualizar.
    :return: HttpResponse con el formulario de edición o redirección al home tras actualización exitosa.
    """
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('home')
    else:
        form = UserForm(instance=user)
    return render(request, 'migrationsdb/user_form.html', {'form': form, 'user': user})

@login_required
@permission_required('migrationsdb.delete_user', raise_exception=True)
def delete_user(request, user_id):
    """
    Elimina un usuario específico de la base de datos y redirige al home.
    :param request: El objeto HttpRequest de Django.
    :param user_id: ID del usuario a eliminar.
    :return: HttpResponse que redirige al home con mensaje de confirmación.
    """
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'Usuario eliminado exitosamente.')
    return redirect('home')

@login_required
@permission_required('migrationsdb.view_book', raise_exception=True)
def list_authors(request):
    """
    Muestra una lista de todos los autores en la base de datos.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el template authors_list.html y la lista de autores.
    """
    authors = Author.objects.all().order_by('last_name', 'first_name')
    return render(request, 'migrationsdb/authors_list.html', {'authors': authors})

@login_required
@permission_required('migrationsdb.add_book', raise_exception=True)
def create_author(request):
    """
    Maneja la creación de un nuevo autor. Muestra el formulario en GET y procesa los datos en POST.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el formulario de autor o redirección a la lista de autores tras creación exitosa.
    """
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Autor creado exitosamente.')
            return redirect('list_authors')
    else:
        form = AuthorForm()
    return render(request, 'migrationsdb/author_form.html', {'form': form})


@login_required
@permission_required('migrationsdb.change_book', raise_exception=True)
def update_author(request, author_id):
    """
    Maneja la actualización de un autor existente. Busca el autor por ID y permite editarlo.
    :param request: El objeto HttpRequest de Django.
    :param author_id: ID del autor a actualizar.
    :return: HttpResponse con el formulario de edición o redirección a la lista de autores tras actualización exitosa.
    """
    author = get_object_or_404(Author, id=author_id)

    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, 'Autor actualizado exitosamente.')
            return redirect('list_authors')
    else:
        form = AuthorForm(instance=author)
    return render(request, 'migrationsdb/author_form.html', {'form': form, 'author': author})


@login_required
@permission_required('migrationsdb.delete_book', raise_exception=True)
def delete_author(request, author_id):
    """
    Elimina un autor específico de la base de datos y redirige a la lista de autores.
    :param request: El objeto HttpRequest de Django.
    :param author_id: ID del autor a eliminar.
    :return: HttpResponse que redirige a la lista de autores con mensaje de confirmación.
    """
    author = get_object_or_404(Author, id=author_id)
    author.delete()
    messages.success(request, 'Autor eliminado exitosamente.')
    return redirect('list_authors')

def list_genres(request):
    """
    Muestra una lista de todos los géneros en la base de datos.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el template genres_list.html y la lista de géneros.
    """
    genres = Genre.objects.all().order_by('name')
    return render(request, 'migrationsdb/genres_list.html', {'genres': genres})

def create_genre(request):
    """
    Maneja la creación de un nuevo género. Muestra el formulario en GET y procesa los datos en POST.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el formulario de género o redirección a la lista de géneros tras creación exitosa.
    """
    if request.method == 'POST':
        form = GenreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Género creado exitosamente.')
            return redirect('list_genres')
    else:
        form = GenreForm()
    return render(request, 'migrationsdb/genre_form.html', {'form': form})

def update_genre(request, genre_id):
    """
    Maneja la actualización de un género existente. Busca el género por ID y permite editarlo.
    :param request: El objeto HttpRequest de Django.
    :param genre_id: ID del género a actualizar.
    :return: HttpResponse con el formulario de edición o redirección a la lista de géneros tras actualización exitosa.
    """
    genre = get_object_or_404(Genre, id=genre_id)

    if request.method == 'POST':
        form = GenreForm(request.POST, instance=genre)
        if form.is_valid():
            form.save()
            messages.success(request, 'Género actualizado exitosamente.')
            return redirect('list_genres')
        else:
            form = GenreForm(instance=genre)
        return render(request, 'migrationsdb/genre_form.html', {'form': form, 'genre': genre})

    form = GenreForm(instance=genre)
    return render(request, 'migrationsdb/genre_form.html', {'form': form, 'genre': genre})

def delete_genre(request, genre_id):
    """
    Elimina un género específico de la base de datos y redirige a la lista de géneros.
    :param request: El objeto HttpRequest de Django.
    :param genre_id: ID del género a eliminar.
    :return: HttpResponse que redirige a la lista de géneros con mensaje de confirmación.
    """
    genre = get_object_or_404(Genre, id=genre_id)
    genre.delete()
    messages.success(request, 'Género eliminado exitosamente.')
    return redirect('list_genres')

@login_required
@permission_required('migrationsdb.view_book', raise_exception=True)
def list_book(request):
    """
    Muestra una lista de todos los libros en la base de datos.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el template books_list.html y la lista de libros.
    """
    books = Book.objects.select_related('author', 'owner').prefetch_related('genres').order_by('title')
    return render(request, 'migrationsdb/books_list.html', {'books': books})

@login_required
@permission_required('migrationsdb.add_book', raise_exception=True)
def create_book(request):
    """
    Maneja la creación de un nuevo libro. Muestra el formulario en GET y procesa los datos en POST.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el formulario de libro o redirección a la lista de libros tras creación exitosa.
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = None  # Sin propietario al crear
            book.save()
            form.save_m2m()  # Guardar relaciones many-to-many
            messages.success(request, 'Libro creado exitosamente.')
            return redirect('list_book')
    else:
        form = BookForm()
    return render(request, 'migrationsdb/book_form.html', {'form': form})

@login_required
@permission_required('migrationsdb.change_book', raise_exception=True)
def update_book(request, book_id):
    """
    Maneja la actualización de un libro existente. Busca el libro por ID y permite editarlo.
    :param request: El objeto HttpRequest de Django.
    :param book_id: ID del libro a actualizar.
    :return: HttpResponse con el formulario de edición o redirección a la lista de libros tras actualización exitosa.
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Libro actualizado exitosamente.')
            return redirect('list_book')
    else:
        form = BookForm(instance=book)
    return render(request, 'migrationsdb/book_form.html', {'form': form, 'book': book})


@login_required
@permission_required('migrationsdb.delete_book', raise_exception=True)
def delete_book(request, book_id):
    """
    Elimina un libro específico de la base de datos y redirige a la lista de libros.
    :param request: El objeto HttpRequest de Django.
    :param book_id: ID del libro a eliminar.
    :return: HttpResponse que redirige a la lista de libros con mensaje de confirmación.
    """
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    messages.success(request, 'Libro eliminado exitosamente.')
    return redirect('list_book')


@library_access_required
def user_library(request, user_id):
    """
    Muestra la biblioteca de un usuario específico, listando todos los libros que posee.
    :param request: El objeto HttpRequest de Django.
    :param user_id: ID del usuario cuya biblioteca se desea ver.
    :return: HttpResponse con el template user_library.html y la lista de libros del usuario.
    """
    user = get_object_or_404(User, id=user_id)
    books = Book.objects.filter(owner=user).select_related('author').prefetch_related('genres').order_by('title')
    return render(request, 'migrationsdb/user_library.html', {'user': user, 'books': books})


@library_access_required
def add_books_to_library(request, user_id):
    """
    Permite agregar libros a la biblioteca de un usuario específico.
    Solo muestra libros que no tienen propietario (owner=None).
    :param request: El objeto HttpRequest de Django.
    :param user_id: ID del usuario al que se le agregarán libros.
    :return: HttpResponse con el formulario para agregar libros o redirección a la biblioteca del usuario tras éxito.
    """
    user = get_object_or_404(User, id=user_id)
    # Solo mostrar libros que NO tienen propietario
    available_books = Book.objects.filter(owner=None).select_related('author').prefetch_related('genres')

    if request.method == 'POST':
        selected_books = request.POST.getlist('books')
        books_added = 0
        books_not_available = []

        for book_id in selected_books:
            book = get_object_or_404(Book, id=book_id)
            # Verificar que el libro sigue disponible antes de asignarlo
            if book.owner is None:
                book.owner = user
                book.save()
                books_added += 1
            else:
                books_not_available.append(book.title)

        # Mensajes informativos
        if books_added > 0:
            messages.success(request, f'{books_added} libro(s) agregado(s) a la biblioteca de {user.first_name}.')

        if books_not_available:
            messages.warning(request,
                             f'Los siguientes libros ya no están disponibles: {", ".join(books_not_available)}')

        return redirect('user_library', user_id=user.id)

    return render(request, 'migrationsdb/add_books_to_library.html', {
        'user': user,
        'available_books': available_books
    })

@library_management_required
def remove_books_from_library(request, user_id):
    """
    Permite quitar libros de la biblioteca de un usuario específico.
    :param request: El objeto HttpRequest de Django.
    :param user_id: ID del usuario del que se quitarán libros.
    :return: HttpResponse con el formulario para quitar libros o redirección a la biblioteca del usuario tras éxito.
    """
    user = get_object_or_404(User, id=user_id)
    user_books = Book.objects.filter(owner=user)

    if request.method == 'POST':
        selected_books = request.POST.getlist('books')
        for book_id in selected_books:
            book = get_object_or_404(Book, id=book_id, owner=user)
            book.owner = None  # Quitar propietario
            book.save()
        messages.success(request, f'Libros removidos de la biblioteca de {user.first_name}.')
        return redirect('user_library', user_id=user.id)

    return render(request, 'migrationsdb/remove_books_from_library.html', {
        'user': user,
        'user_books': user_books
    })


def user_library_pdf(request, user_id):
    """
    Genera un PDF con la lista de libros en la biblioteca de un usuario específico.
    :param request: El objeto HttpRequest de Django.
    :param user_id: ID del usuario cuya biblioteca se desea exportar a PDF.
    :return: HttpResponse con el PDF generado o redirección a la biblioteca del usuario con mensaje de error.
    :technology: Utiliza xhtml2pdf para convertir una plantilla HTML en PDF.
    """
    print(f"[views.user_library_pdf] Solicitud PDF para user_id={user_id}")
    user = get_object_or_404(User, id=user_id)
    books = user.books.select_related('author').prefetch_related('genres')
    if not books.exists():
        messages.warning(request, 'No hay libros en la biblioteca para generar PDF.')
        return redirect('user_library', user_id=user.id)

    response = pdf_services.user_library_pdf(user, books)
    if response is None:
        return HttpResponse('Error al generar PDF', status=400)
    return response

def books_report_pdf(request):
    """
    Genera un PDF con un reporte de todos los libros en la base de datos.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el PDF generado.
    """
    books = Book.objects.select_related('author', 'owner').prefetch_related('genres')
    return pdf_services.books_report_pdf(books)

def search_external_books(request):
    """
    Busca libros en Open Library y muestra resultados paginados.
    Admite parámetros GET:
    - q: término de búsqueda (requerido)
    - page: página (1..N, por defecto 1)
    - page_size: tamaño de página (1..100, por defecto 20)
    - owner_id: ID de usuario para asignar al importar (opcional)
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el template book_search.html y los resultados de la búsqueda.
    """

    # Obtener parámetros de búsqueda
    q = request.GET.get("q", "").strip()
    owner_id = request.GET.get("owner_id")
    page = int(request.GET.get("page", "1") or 1)
    page_size = int(request.GET.get("page_size", "20") or 20)

    # Validar página y tamaño de página
    data = {"items": [], "page": page, "next": None, "prev": None, "total": 0}

    # Realizar búsqueda si hay término
    if q:
        try:
            data = ol_search(q=q, page=page, page_size=page_size)
        except Exception as e:
            messages.warning(request, f"No se pudo consultar Open Library: {e}")

    # Preparar contexto para el template
    ctx = {
        "q": q,
        "page": data["page"],
        "next": data["next"],
        "prev": data["prev"],
        "total": data["total"],
        "results": data["items"],
        "owner_id": owner_id,
        "page_size": page_size,
        "page_size_options": [5, 10, 20],
    }
    return render(request, 'migrationsdb/book_search.html', ctx)

def _split_author(full_name: str):
    """
    Divide un nombre completo en (last_name, first_name) simple.
    Si solo hay un nombre, last_name es ese nombre y first_name es vacío.
    Si está vacío, devuelve ("Desconocido", "Autor").
    :param full_name: Nombre completo del autor.
    :return: Tupla (last_name, first_name)
    """
    parts = (full_name or "").strip().split()
    if not parts:
        return "Desconocido", "Autor"
    if len(parts) == 1:
        return parts[0], ""
    return parts[-1], " ".join(parts[:-1])


@transaction.atomic
def import_external_book(request, isbn: str):
    """
    Importa un libro desde Open Library, con o sin ISBN.
    Si no hay ISBN, usa parámetros GET 'title' y 'author' para crear el libro.
    Evita duplicados por ISBN o por título+primer autor.
    Parámetros GET opcionales:
    - owner_id: ID de usuario para asignar como propietario (opcional)
    :param request: El objeto HttpRequest de Django.
    :param isbn: ISBN del libro a importar, o 'no-isbn' si no tiene.
    :return: HttpResponse que redirige a la biblioteca del usuario o a la lista de libros.
    :technology: Utiliza el servicio openlibrary_service para obtener datos del libro.
    """
    try:
        # Si no hay ISBN, usar parámetros de título y autor para buscar
        if isbn == 'no-isbn':
            title = request.GET.get('title', '').strip()
            author = request.GET.get('author', '').strip()
            if not title:
                messages.error(request, "No se puede importar libro sin título.")
                return redirect('search_external_books')

            # Crear libro directamente con los datos disponibles
            book = {
                "title": title,
                "authors": [author] if author else ["Autor Desconocido"],
                "year": None,
                "isbn": None,
                "pages": None,
                "subjects": []
            }
        else:
            book = ol_get_by_isbn(isbn)
            if not book:
                messages.error(request, "Libro no encontrado en Open Library.")
                return redirect('search_external_books')

        # Usar título + primer autor como identificador alternativo si no hay ISBN
        isbn_clean = str(book["isbn"])[:13] if book.get("isbn") else None
        title_clean = (book["title"] or "Sin título")[:200]

        # Verificar duplicados por ISBN o por título+autor
        existing = None
        if isbn_clean:
            existing = Book.objects.filter(isbn=isbn_clean).first()

        if not existing:
            author_name = (book["authors"][0] if book["authors"] else "Autor Desconocido").strip()
            existing = Book.objects.filter(
                title__iexact=title_clean,
                author__first_name__icontains=author_name.split()[-1] if author_name else ""
            ).first()

        if existing:
            messages.info(request, f"El libro '{existing.title}' ya existe en el sistema.")
            owner_id = request.GET.get("owner_id")
            if owner_id:
                return redirect('user_library', user_id=owner_id)
            return redirect('list_book')

        # Crear/obtener autor
        author_name = (book["authors"][0] if book["authors"] else "Autor Desconocido").strip()
        ln, fn = _split_author(author_name)
        author, _ = Author.objects.get_or_create(
            first_name=fn or "N/A",
            last_name=ln or "N/A",
            defaults={
                "birth_date": date(1900, 1, 1),
                "nationality": "N/D",
            }
        )

        # Crear géneros
        genres = []
        for s in (book.get("subjects") or [])[:5]:
            name = str(s)[:50]
            g, _ = Genre.objects.get_or_create(name=name, defaults={"description": ""})
            genres.append(g)

        # Fecha y páginas
        year = book.get("year")
        pub_date = date(int(year), 1, 1) if isinstance(year, int) and 1 <= year <= 9999 else date(1900, 1, 1)
        pages = int(book["pages"]) if str(book.get("pages", "")).isdigit() else 100

        # Obtener owner si se especifica
        owner = None
        owner_id = request.GET.get("owner_id")
        if owner_id:
            try:
                owner = User.objects.get(id=int(owner_id))
            except Exception:
                owner = None

        # Crear libro
        new_book = Book(
            title=title_clean,
            author=author,
            owner=owner,
            published_date=pub_date,
            isbn=isbn_clean,
            pages=pages,
        )

        new_book.save()
        if genres:
            new_book.genres.set(genres)

        messages.success(request, f"Libro importado: {new_book.title}")
        if owner:
            return redirect('user_library', user_id=owner.id)
        return redirect('list_book')

    except Exception as e:
        messages.error(request, f"Error al importar: {e}")
        return redirect('search_external_books')


def register_view(request):
    """
    Vista de registro de usuarios con asignación automática al grupo 'Lectores'.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        age = request.POST.get('age')

        # Validar que no exista el usuario
        if AuthUser.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'registration/register.html')

        try:
            # Crear usuario de autenticación
            auth_user = AuthUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # Crear usuario de biblioteca
            user = User.objects.create(
                auth_user=auth_user,
                first_name=first_name,
                last_name=last_name,
                age=int(age),
                email=email
            )

            # Asignar al grupo 'Lectores'
            lectores_group, _ = Group.objects.get_or_create(name='Lectores')
            auth_user.groups.add(lectores_group)

            # Login automático
            login(request, auth_user)
            messages.success(request, f'Bienvenido {first_name}! Tu cuenta ha sido creada exitosamente.')
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {e}')

    return render(request, 'registration/register.html')

def login_view(request):
    """
    Vista de login personalizada.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Credenciales inválidas.')

    return render(request, 'registration/login.html')


def logout_view(request):
    """
    Vista de logout.
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

@user_passes_test(lambda u: u.is_superuser)
def setup_groups(request):
    """
    Vista para configurar los grupos por defecto. Solo para superusuarios.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el template setup_groups.html o redirección tras configuración.
    """
    if request.method == 'POST':
        try:
            created_groups = setup_default_groups()
            if created_groups:
                messages.success(request, f'Grupos creados exitosamente: {", ".join(created_groups)}')
            else:
                messages.info(request, 'Todos los grupos ya existían. Se actualizaron sus permisos.')
        except Exception as e:
            messages.error(request, f'Error al configurar grupos: {str(e)}')

        return redirect('setup_groups')

    # Obtener información de grupos existentes
    groups = Group.objects.prefetch_related('permissions').all()

    context = {
        'groups': groups,
        'total_groups': groups.count(),
    }

    return render(request, 'migrationsdb/setup_groups.html', context)


def setup_default_groups():
    """
    Función auxiliar para configurar grupos por defecto.
    Usada por la vista setup_groups.
    :return: Lista de nombres de grupos que fueron creados.
    """
    from django.core.management import call_command
    from io import StringIO
    import sys

    # Capturar la salida del comando
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        call_command('setup_initial_groups')
        output = captured_output.getvalue()

        # Extraer los grupos creados del output
        created_groups = []
        for line in output.split('\n'):
            if '✓ Grupo' in line and 'creado' in line:
                group_name = line.split('"')[1]
                created_groups.append(group_name)

        return created_groups

    finally:
        sys.stdout = old_stdout


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Administradores').exists())
def manage_user_permissions(request, user_id):
    """
    Vista para que administradores gestionen permisos de usuarios.
    """
    # Obtener el usuario de biblioteca primero
    try:
        library_user = get_object_or_404(User, id=user_id)

        # Verificar si tiene usuario de autenticación asociado
        if not library_user.auth_user:
            messages.error(request, 'Este usuario no tiene acceso al sistema.')
            return redirect('home')

        auth_user = library_user.auth_user

    except User.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('home')

    if request.method == 'POST':
        # Procesar cambios de grupos
        selected_groups = request.POST.getlist('groups')
        auth_user.groups.clear()

        for group_id in selected_groups:
            try:
                group = Group.objects.get(id=group_id)
                auth_user.groups.add(group)
            except Group.DoesNotExist:
                pass

        messages.success(request, f'Permisos actualizados para {auth_user.get_full_name() or auth_user.username}')
        return redirect('manage_user_permissions', user_id=user_id)

    # Obtener todos los grupos disponibles
    all_groups = Group.objects.all().order_by('name')
    user_groups = auth_user.groups.all()

    context = {
        'auth_user': auth_user,
        'library_user': library_user,
        'all_groups': all_groups,
        'user_groups': user_groups,
    }

    return render(request, 'migrationsdb/manage_permissions.html', context)


@require_http_methods(["POST"])
@login_required
def update_genre_api(request, genre_id):
    try:
        if not request.user.has_perm('migrationsdb.change_genre'):
            return JsonResponse({'error': 'No tienes permisos'}, status=403)

        genre = get_object_or_404(Genre, id=genre_id)

        # Usar el serializer para validación y actualización
        serializer = GenreSerializer(genre, data=request.POST, partial=True)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                'success': True,
                'message': f'Género "{serializer.data["name"]}" actualizado correctamente',
                'genre': serializer.data
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': serializer.errors
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)