# Create your models here.
from django.db import models

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Author(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100, verbose_name='Nombre')
    last_name = models.CharField(max_length=100, verbose_name='Apellido')
    birth_date = models.DateField(verbose_name='Fecha de nacimiento')
    nationality = models.CharField(max_length=50, verbose_name='Nacionalidad')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Genre(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name='Género')
    description = models.TextField(blank=True, verbose_name='Descripción')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='Título')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books', verbose_name='Autor')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books',verbose_name='Propietario', null=True, blank=True)
    published_date = models.DateField(verbose_name='Fecha de publicación')
    isbn = models.CharField(max_length=13, unique=True, verbose_name='ISBN')
    pages = models.IntegerField(verbose_name='Número de páginas')
    genres = models.ManyToManyField('Genre', blank=False, verbose_name='Géneros')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
