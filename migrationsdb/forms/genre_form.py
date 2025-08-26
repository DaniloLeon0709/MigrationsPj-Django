from django import forms
from migrationsdb.models import Genre

class GenreForm(forms.ModelForm):
    """
    Formulario para crear y actualizar géneros con validaciones personalizadas.
    """

    class Meta:
        model = Genre
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre del Género',
            'description': 'Descripción',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = f'Ingrese {field.label.lower()}'

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        # Validar que el nombre no esté vacío y tenga al menos 2 caracteres
        if name and len(name.strip()) < 2:
            raise forms.ValidationError('El nombre del género debe tener al menos 2 caracteres.')


        return cleaned_data