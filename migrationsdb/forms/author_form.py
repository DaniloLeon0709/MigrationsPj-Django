from datetime import date
from django import forms
from migrationsdb.models import Author

class AuthorForm(forms.ModelForm):
    """
    Formulario para crear y actualizar autores con validaciones personalizadas.
    """

    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'birth_date', 'nationality']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'birth_date': 'Fecha de Nacimiento',
            'nationality': 'Nacionalidad',}
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = f'Ingrese {field.label.lower()}'

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        birth_date = cleaned_data.get('birth_date')
        # Validar que el nombre y apellido no estén vacíos
        if first_name and len(first_name.strip()) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')

        if last_name and len(last_name.strip()) < 2:
            raise forms.ValidationError('El apellido debe tener al menos 2 caracteres.')

        # Validar que la fecha de nacimiento no sea futura
        if birth_date and birth_date > date.today():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura.')

        # Validar que el autor no sea menor de edad (opcional)
        if birth_date and (date.today() - birth_date).days < 6570:  # ~18 años
            raise forms.ValidationError('El autor debe ser mayor de edad.')

        return cleaned_data
