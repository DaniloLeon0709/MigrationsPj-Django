from datetime import date
from django import forms
from migrationsdb.models import Book

class BookForm(forms.ModelForm):
    """
    Formulario para crear y actualizar libros con validaciones personalizadas.
    """

    class Meta:
        model = Book
        fields = ['title', 'author', 'owner', 'published_date', 'isbn', 'pages', 'genres']
        labels = {
            'title': 'Título',
            'author': 'Autor',
            'published_date': 'Fecha de Publicación',
            'isbn': 'ISBN',
            'pages': 'Número de Páginas',
            'genres': 'Géneros',
        }
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
            'genres': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

            if not field.widget.attrs.get('placeholder') and field_name not in ['author', 'genres']:
                field.widget.attrs['placeholder'] = f'Ingrese {field.label.lower()}'

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        published_date = cleaned_data.get('published_date')
        isbn = cleaned_data.get('isbn')
        pages = cleaned_data.get('pages')

        # Validar que el título no esté vacío y tenga al menos 2 caracteres
        if title and len(title.strip()) < 2:
            raise forms.ValidationError('El título debe tener al menos 2 caracteres.')

        # Validar que la fecha de publicación no sea futura
        if published_date and published_date > date.today():
            raise forms.ValidationError('La fecha de publicación no puede ser futura.')

        # Validar que el ISBN tenga 10 o 13 caracteres
        if isbn and len(isbn) not in [10, 13]:
            raise forms.ValidationError('El ISBN debe tener 10 o 13 caracteres.')

        # Validar que el número de páginas sea positivo
        if pages is not None and pages <= 0:
            raise forms.ValidationError('El número de páginas debe ser un valor positivo.')

        return cleaned_data

