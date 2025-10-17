from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('setup-groups/', views.setup_groups, name='setup_groups'),

    # Usuarios
    path('', views.home, name='home'),
    path('create/', views.create_user, name='create_user'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),

    # Autores
    path('authors/', views.list_authors, name='list_authors'),
    path('authors/create/', views.create_author, name='create_author'),
    path('authors/update/<int:author_id>/', views.update_author, name='update_author'),
    path('authors/delete/<int:author_id>/', views.delete_author, name='delete_author'),

    # Géneros
    path('genres/', views.list_genres, name='list_genres'),
    path('genres/create/', views.create_genre, name='create_genre'),
    #path('genres/update/<int:genre_id>/', views.update_genre, name='update_genre'),
    path('genres/delete/<int:genre_id>/', views.delete_genre, name='delete_genre'),

    # Libros
    path('books/', views.list_book, name='list_book'),
    path('books/create/', views.create_book, name='create_book'),
    path('books/update/<int:book_id>/', views.update_book, name='update_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),

    # Biblioteca de usuarios
    path('users/<int:user_id>/library/', views.user_library, name='user_library'),
    path('users/<int:user_id>/add-books/', views.add_books_to_library, name='add_books_to_library'),
    path('users/<int:user_id>/remove-books/', views.remove_books_from_library, name='remove_books_from_library'),

    # PDFs
    path('users/<int:user_id>/library/pdf/', views.user_library_pdf, name='user_library_pdf'),
    path('books/report/pdf/', views.books_report_pdf, name='books_report_pdf'),

    # Búsqueda externa
    path('search-external-books/', views.search_external_books, name='search_external_books'),
    path('import-external-book/<str:isbn>/', views.import_external_book, name='import_external_book'),

    # Gestión de permisos (solo para administradores)
    path('users/<int:user_id>/permissions/', views.manage_user_permissions, name='manage_user_permissions'),

# API REST
# En la sección de URLs existentes, agrega:
path('api/genres/<int:genre_id>/update/', views.update_genre_api, name='update_genre_api'),]