from django.urls import path
from migrationsdb import views

urlpatterns = [
    # Usuarios
    path('', views.home, name='home'),
    path('user/create/', views.create_user, name='create_user'),
    path('user/update/<int:user_id>/', views.update_user, name='update_user'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user/<int:user_id>/library/', views.user_library, name='user_library'),
    path('user/<int:user_id>/add-books/', views.add_books_to_library, name='add_books_to_library'),

    # Autores
    path('authors/', views.list_authors, name='list_authors'),
    path('author/create/', views.create_author, name='create_author'),
    path('author/update/<int:author_id>/', views.update_author, name='update_author'),
    path('author/delete/<int:author_id>/', views.delete_author, name='delete_author'),

    # Géneros
    path('genres/', views.list_genres, name='list_genres'),
    path('genre/create/', views.create_genre, name='create_genre'),
    path('genre/update/<int:genre_id>/', views.update_genre, name='update_genre'),
    path('genre/delete/<int:genre_id>/', views.delete_genre, name='delete_genre'),

    # Libros
    path('books/', views.list_book, name='list_book'),
    path('book/create/', views.create_book, name='create_book'),
    path('book/update/<int:book_id>/', views.update_book, name='update_book'),
    path('book/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('user/<int:user_id>/remove-books/', views.remove_books_from_library, name='remove_books_from_library'),

]