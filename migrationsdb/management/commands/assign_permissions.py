from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission


class Command(BaseCommand):
    """"
    Asigna permisos o grupos a usuarios existentes
    Uso:
    python manage.py assign_permissions --username <username> [--group <groupname>] [--permission <app_label.codename>]
    Ejemplo:
    python manage.py assign_permissions --username admin --group Administradores
    python manage.py assign_permissions --username user1 --permission migrationsdb.view_all_libraries
    """
    help = 'Asignar permisos o grupos a usuarios'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True)
        parser.add_argument('--group', type=str)
        parser.add_argument('--permission', type=str)

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)

            if options['group']:
                group = Group.objects.get(name=options['group'])
                user.groups.add(group)
                self.stdout.write(f'✓ Usuario {username} agregado al grupo {group.name}')

            if options['permission']:
                perm_parts = options['permission'].split('.')
                if len(perm_parts) == 2:
                    app_label, codename = perm_parts
                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename
                    )
                    user.user_permissions.add(permission)
                    self.stdout.write(f'Permiso {permission.name} asignado a {username}')

        except Exception as e:
            self.stdout.write(f'Error: {str(e)}')