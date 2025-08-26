from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from migrationsdb.forms import UserForm, AuthorForm, GenreForm, BookForm
from migrationsdb.models import User, Author, Genre, Book

def home(request):
    """
    Muestra la página principal con la lista de todos los usuarios ordenados por fecha de creación.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el template home.html y la lista de usuarios.
    """
    users = User.objects.all().order_by('last_name', 'first_name')
    return render(request, 'migrationsdb/home.html', {'users': users})

def create_user(request):
    """
    Maneja la creación de un nuevo usuario. Muestra el formulario en GET y procesa los datos en POST.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el formulario de usuario o redirección al home tras creación exitosa.
    """
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('home')
    else:
        form = UserForm()
    return render(request, 'migrationsdb/user_form.html', {'form': form})

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

def list_authors(request):
    """
    Muestra una lista de todos los autores en la base de datos.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el template authors_list.html y la lista de autores.
    """
    authors = Author.objects.all().order_by('last_name', 'first_name')
    return render(request, 'migrationsdb/authors_list.html', {'authors': authors})

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

def list_book(request):
    """
    Muestra una lista de todos los libros en la base de datos.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el template books_list.html y la lista de libros.
    """
    books = Book.objects.select_related('author', 'owner').prefetch_related('genres').order_by('title')
    return render(request, 'migrationsdb/books_list.html', {'books': books})

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

