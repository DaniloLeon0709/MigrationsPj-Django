from django import forms
from migrationsdb.models import User


class UserForm(forms.ModelForm):
    """
    Formulario para crear y actualizar usuarios con validaciones personalizadas.
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'age', 'email']
        labels = {
            'first_name': 'Primer Nombre',
            'last_name': 'Apellido',
            'age': 'Edad',
            'email': 'Correo Electrónico',
        }

    def clean_first_name(self):
        """
        Valida que el primer nombre no esté vacío.
        :return: El primer nombre limpio.
        """
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError("El nombre es necesario.")
        return first_name

    def clean_last_name(self):
        """
        Valida que el apellido no esté vacío.
        :return: El apellido limpio.
        """
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError("El apellido es necesario.")
        return last_name

    def clean_age(self):
        """
        Valida que la edad sea positiva y mayor a 18 años.
        :return: La edad validada.
        """
        age = self.cleaned_data.get('age')
        if age is not None and age < 0 or age > 100:
            raise forms.ValidationError("Rango de edad inválido.")
        if age is not None and age < 18:
            raise forms.ValidationError("El usuario debe ser mayor de 18 años.")
        return age

    def clean_email(self):
        """
        Válida que el email sea único, excluyendo la instancia actual en caso de edición.
        :return: El email validado.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.id if self.instance else None).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario añadiendo clases Bootstrap a los campos.
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 3
            else:
                field.widget.attrs['class'] = 'form-control'

            if not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = f'Ingrese {field.label.lower()}'