from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from migrationsdb.models import User, Author, Genre, Book

class HasAuthUserFilter(admin.SimpleListFilter):
    title = _('Estado de acceso al sistema')
    parameter_name = 'has_auth_user'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Puede acceder al sistema')),
            ('no', _('Solo biblioteca')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(auth_user__isnull=False)
        if self.value() == 'no':
            return queryset.filter(auth_user__isnull=True)
        return queryset

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'age', 'has_auth_user', 'books_count', 'created_at']
    list_filter = ['age', 'created_at', HasAuthUserFilter]
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['created_at']
    ordering = ['last_name', 'first_name']

    def has_auth_user(self, obj):
        return obj.auth_user is not None
    has_auth_user.boolean = True
    has_auth_user.short_description = 'Puede acceder'

    def books_count(self, obj):
        return obj.books.count()
    books_count.short_description = 'Libros'

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'birth_date', 'nationality', 'books_count', 'created_at']
    list_filter = ['nationality', 'birth_date', 'created_at']
    search_fields = ['first_name', 'last_name', 'nationality']
    readonly_fields = ['created_at']
    ordering = ['last_name', 'first_name']

    def books_count(self, obj):
        return obj.books.count()
    books_count.short_description = 'Libros'

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'books_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    ordering = ['name']

    def books_count(self, obj):
        return obj.books.count()
    books_count.short_description = 'Libros'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'owner', 'published_date', 'isbn', 'pages', 'created_at']
    list_filter = ['published_date', 'created_at', 'author', 'genres', 'owner']
    search_fields = ['title', 'author__first_name', 'author__last_name', 'isbn']
    readonly_fields = ['created_at']
    filter_horizontal = ['genres']
    ordering = ['title']