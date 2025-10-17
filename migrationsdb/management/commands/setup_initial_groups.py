from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from migrationsdb.models import User, Book, Author, Genre


class Command(BaseCommand):
    help = 'Configura los grupos y permisos por defecto para el sistema de biblioteca'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Resetea todos los grupos existentes antes de crear los nuevos',
        )

    def handle(self, *args, **options):
        try:
            if options['reset']:
                self.stdout.write(
                    self.style.WARNING('Eliminando grupos existentes...')
                )
                Group.objects.all().delete()

            created_groups = self.setup_groups_and_permissions()

            if created_groups:
                self.stdout.write(
                    self.style.SUCCESS(f'Grupos creados exitosamente: {", ".join(created_groups)}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Todos los grupos ya existían. Permisos actualizados.')
                )

        except Exception as e:
            raise CommandError(f'Error al configurar grupos: {str(e)}')

    def setup_groups_and_permissions(self):
        """Configura los grupos por defecto con sus permisos correspondientes."""
        created_groups = []

        # Obtener tipos de contenido
        user_ct = ContentType.objects.get_for_model(User)
        book_ct = ContentType.objects.get_for_model(Book)
        author_ct = ContentType.objects.get_for_model(Author)
        genre_ct = ContentType.objects.get_for_model(Genre)

        # Definición de grupos y permisos (usando app_label.codename)
        groups_config = {
            'Administradores': {
                'description': 'Acceso completo al sistema',
                'permissions': [
                    # Usuarios
                    ('migrationsdb', 'add_user'),
                    ('migrationsdb', 'change_user'),
                    ('migrationsdb', 'delete_user'),
                    ('migrationsdb', 'view_user'),
                    # Libros
                    ('migrationsdb', 'add_book'),
                    ('migrationsdb', 'change_book'),
                    ('migrationsdb', 'delete_book'),
                    ('migrationsdb', 'view_book'),
                    # Autores
                    ('migrationsdb', 'add_author'),
                    ('migrationsdb', 'change_author'),
                    ('migrationsdb', 'delete_author'),
                    ('migrationsdb', 'view_author'),
                    # Géneros
                    ('migrationsdb', 'add_genre'),
                    ('migrationsdb', 'change_genre'),
                    ('migrationsdb', 'delete_genre'),
                    ('migrationsdb', 'view_genre'),
                    # Permisos personalizados
                    ('migrationsdb', 'view_all_libraries'),
                    ('migrationsdb', 'manage_library'),
                    ('migrationsdb', 'generate_reports'),
                    ('migrationsdb', 'import_books'),
                ]
            },
            'Bibliotecarios': {
                'description': 'Gestión de libros y bibliotecas de usuarios',
                'permissions': [
                    # Solo visualización de usuarios
                    ('migrationsdb', 'view_user'),
                    # Gestión completa de libros
                    ('migrationsdb', 'add_book'),
                    ('migrationsdb', 'change_book'),
                    ('migrationsdb', 'delete_book'),
                    ('migrationsdb', 'view_book'),
                    # Gestión de autores y géneros
                    ('migrationsdb', 'add_author'),
                    ('migrationsdb', 'change_author'),
                    ('migrationsdb', 'delete_author'),
                    ('migrationsdb', 'view_author'),
                    ('migrationsdb', 'add_genre'),
                    ('migrationsdb', 'change_genre'),
                    ('migrationsdb', 'delete_genre'),
                    ('migrationsdb', 'view_genre'),
                    # Permisos especiales
                    ('migrationsdb', 'view_all_libraries'),
                    ('migrationsdb', 'manage_library'),
                    ('migrationsdb', 'generate_reports'),
                    ('migrationsdb', 'import_books'),
                ]
            },
            'Lectores': {
                'description': 'Acceso básico para gestionar su propia biblioteca',
                'permissions': [
                    # Solo ver libros y autores
                    ('migrationsdb', 'view_book'),
                    ('migrationsdb', 'view_author'),
                    ('migrationsdb', 'view_genre'),
                    # No pueden ver otros usuarios
                ]
            },
            'Invitados': {
                'description': 'Acceso de solo lectura',
                'permissions': [
                    ('migrationsdb', 'view_book'),
                    ('migrationsdb', 'view_author'),
                    ('migrationsdb', 'view_genre'),
                ]
            }
        }

        # Crear grupos y asignar permisos
        for group_name, config in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                created_groups.append(group_name)
                self.stdout.write(f'✓ Grupo "{group_name}" creado')
            else:
                self.stdout.write(f'→ Grupo "{group_name}" ya existe, actualizando permisos')

            # Limpiar permisos existentes
            group.permissions.clear()

            # Asignar permisos
            permissions_added = 0
            for app_label, codename in config['permissions']:
                try:
                    # Obtener el content_type específico según el modelo
                    if codename.endswith('_user'):
                        content_type = user_ct
                    elif codename.endswith('_book'):
                        content_type = book_ct
                    elif codename.endswith('_author'):
                        content_type = author_ct
                    elif codename.endswith('_genre'):
                        content_type = genre_ct
                    else:
                        # Para permisos personalizados, usar el content_type de User
                        content_type = user_ct

                    permission = Permission.objects.get(
                        codename=codename,
                        content_type=content_type
                    )
                    group.permissions.add(permission)
                    permissions_added += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  Permiso no encontrado: {app_label}.{codename}')
                    )
                except Permission.MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.WARNING(f'  Múltiples permisos encontrados para: {app_label}.{codename}')
                    )

            self.stdout.write(f'  → {permissions_added} permisos asignados')

        return created_groups