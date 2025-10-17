# Create your models here.
from django.db import models
from django.contrib.auth.models import User as AuthUser

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario del Sistema')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def can_login(self):
        """Indica si este usuario puede iniciar sesión"""
        return self.auth_user is not None

    @property
    def username(self):
        """Retorna el username del usuario de autenticación si existe"""
        return self.auth_user.username if self.auth_user else None

    def create_auth_user(self, username, password):
        """Crea un usuario de autenticación asociado"""
        if not self.auth_user:
            auth_user = AuthUser.objects.create_user(
                username=username,
                email=self.email,
                password=password,
                first_name=self.first_name,
                last_name=self.last_name
            )
            self.auth_user = auth_user
            self.save()
            return auth_user
        return self.auth_user

    # Permisos personalizados
    class Meta:
        permissions = [
            ("view_all_libraries", "Puede ver todas las bibliotecas"),
            ("manage_library", "Puede gestionar bibliotecas de usuarios"),
            ("generate_reports", "Puede generar reportes PDF"),
            ("import_books", "Puede importar libros externos"),
        ]

    def is_administrator(self):
        """Verifica si el usuario es administrador"""
        if not self.auth_user:
            return False
        return self.auth_user.groups.filter(name='Administradores').exists()

    def is_librarian(self):
        """Verifica si el usuario es bibliotecario"""
        if not self.auth_user:
            return False
        return self.auth_user.groups.filter(name='Bibliotecarios').exists()

    def has_group(self, group_name):
        """Verifica si el usuario pertenece a un grupo específico"""
        if not self.auth_user:
            return False
        return self.auth_user.groups.filter(name=group_name).exists()

class Author(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100, verbose_name='Primer Nombre')
    last_name = models.CharField(max_length=100, verbose_name='Apellido')
    birth_date = models.DateField(verbose_name='Fecha de nacimiento')
    nationality = models.CharField(max_length=100, verbose_name='Nacionalidad')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

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
    isbn = models.CharField(max_length=13, unique=True, verbose_name='ISBN', null=True, blank=True)
    pages = models.IntegerField(verbose_name='Número de páginas')
    genres = models.ManyToManyField('Genre', blank=False, verbose_name='Géneros')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
