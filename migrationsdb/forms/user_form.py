from django import forms
from django.contrib.auth.models import User as AuthUser
from migrationsdb.models import User


class UserForm(forms.ModelForm):
    """
    Formulario para crear y actualizar usuarios con validaciones personalizadas.
    Incluye campos opcionales para crear usuario de autenticación asociado.
    """

    # Campos adicionales para autenticación (opcionales)
    create_auth_user = forms.BooleanField(
        required=False,
        label='Crear usuario de acceso al sistema',
        help_text='Permite que este usuario pueda iniciar sesión'
    )
    username = forms.CharField(
        max_length=150,
        required=False,
        label='Nombre de usuario',
        help_text='Nombre para iniciar sesión (solo si se marca la opción anterior)'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='Contraseña',
        help_text='Contraseña para iniciar sesión (solo si se marca la opción anterior)'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label='Confirmar contraseña'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'age', 'email']
        labels = {
            'first_name': 'Primer Nombre',
            'last_name': 'Apellido',
            'age': 'Edad',
            'email': 'Correo Electrónico',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa el primer nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa el apellido'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y configura widgets y atributos de Bootstrap.
        También maneja la lógica de actualización vs creación de usuarios.
        """
        super().__init__(*args, **kwargs)

        # Aplicar clases Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        # Configuraciones específicas por campo
        self.fields['first_name'].widget.attrs.update({
            'placeholder': 'Ej: Juan Carlos',
            'autocomplete': 'given-name'
        })

        self.fields['last_name'].widget.attrs.update({
            'placeholder': 'Ej: García López',
            'autocomplete': 'family-name'
        })

        self.fields['age'].widget.attrs.update({
            'type': 'number',
            'min': '0',
            'max': '100',
            'placeholder': 'Ej: 25'
        })

        self.fields['email'].widget.attrs.update({
            'type': 'email',
            'placeholder': 'ejemplo@correo.com',
            'autocomplete': 'email'
        })

        self.fields['username'].widget.attrs.update({
            'placeholder': 'usuario123',
            'autocomplete': 'username',
            'minlength': '3'
        })

        self.fields['password'].widget.attrs.update({
            'placeholder': 'Mínimo 6 caracteres',
            'autocomplete': 'new-password',
            'minlength': '6'
        })

        self.fields['password_confirm'].widget.attrs.update({
            'placeholder': 'Confirmar contraseña',
            'autocomplete': 'new-password'
        })

        # Si es actualización, prellenar datos de autenticación si existen
        if self.instance and self.instance.pk and self.instance.auth_user:
            self.fields['create_auth_user'].initial = True
            self.fields['username'].initial = self.instance.auth_user.username
            # No prellenar contraseñas por seguridad

    def clean(self):
        """
        Realiza todas las validaciones del formulario de forma centralizada.
        Valida datos básicos del usuario y datos de autenticación si se solicita.
        :return: Los datos limpios del formulario.
        """
        cleaned_data = super().clean()

        # Validaciones de campos básicos
        first_name = cleaned_data.get('first_name', '').strip()
        last_name = cleaned_data.get('last_name', '').strip()
        age = cleaned_data.get('age')
        email = cleaned_data.get('email', '').strip()

        # Validar primer nombre
        if not first_name:
            self.add_error('first_name', 'El primer nombre es obligatorio.')
        elif len(first_name) < 2:
            self.add_error('first_name', 'El primer nombre debe tener al menos 2 caracteres.')
        elif not first_name.replace(' ', '').isalpha():
            self.add_error('first_name', 'El primer nombre solo puede contener letras y espacios.')

        # Validar apellido
        if not last_name:
            self.add_error('last_name', 'El apellido es obligatorio.')
        elif len(last_name) < 2:
            self.add_error('last_name', 'El apellido debe tener al menos 2 caracteres.')
        elif not last_name.replace(' ', '').isalpha():
            self.add_error('last_name', 'El apellido solo puede contener letras y espacios.')

        # Validar edad
        if age is not None:
            if age < 0 or age > 100:
                self.add_error('age', 'La edad debe estar entre 0 y 100 años.')
            elif age < 18:
                self.add_error('age', 'El usuario debe ser mayor de edad (18 años o más).')

        # Validar email único (solo si no es una actualización del mismo usuario)
        if email:
            existing_user = User.objects.filter(email=email).first()
            if existing_user and existing_user != self.instance:
                self.add_error('email', 'Ya existe un usuario con este correo electrónico.')

        # Validaciones de autenticación
        create_auth = cleaned_data.get('create_auth_user')
        username = cleaned_data.get('username', '').strip()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if create_auth:
            # Validar username requerido
            if not username:
                self.add_error('username', 'Se requiere nombre de usuario para crear acceso al sistema.')
            elif len(username) < 3:
                self.add_error('username', 'El nombre de usuario debe tener al menos 3 caracteres.')
            elif not username.replace('_', '').replace('-', '').isalnum():
                self.add_error('username',
                               'El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.')
            elif AuthUser.objects.filter(username=username).exists():
                # Verificar si no es una actualización del mismo usuario
                if not (self.instance.pk and self.instance.auth_user and self.instance.auth_user.username == username):
                    self.add_error('username', 'El nombre de usuario ya existe.')

            # Validar contraseña requerida
            if not password:
                self.add_error('password', 'Se requiere contraseña para crear acceso al sistema.')
            elif len(password) < 6:
                self.add_error('password', 'La contraseña debe tener al menos 6 caracteres.')

            # Validar confirmación de contraseña
            if not password_confirm:
                self.add_error('password_confirm', 'Debe confirmar la contraseña.')
            elif password != password_confirm:
                self.add_error('password_confirm', 'Las contraseñas no coinciden.')
        else:
            # Si no se va a crear usuario de autenticación, limpiar campos relacionados
            cleaned_data['username'] = ''
            cleaned_data['password'] = ''
            cleaned_data['password_confirm'] = ''

        # Actualizar datos limpios
        cleaned_data['first_name'] = first_name
        cleaned_data['last_name'] = last_name
        cleaned_data['email'] = email

        return cleaned_data

    def save(self, commit=True):
        """
        Guarda el usuario y opcionalmente crea un usuario de autenticación asociado.
        :param commit: Si debe guardar inmediatamente en la base de datos.
        :return: La instancia del usuario guardada.
        """
        user = super().save(commit=False)

        if commit:
            user.save()

            # Crear usuario de autenticación si se solicita
            if self.cleaned_data.get('create_auth_user') and not user.auth_user:
                username = self.cleaned_data.get('username')
                password = self.cleaned_data.get('password')

                if username and password:
                    user.create_auth_user(username, password)

        return user