from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from migrationsdb.forms.user_form import UserForm
from migrationsdb.models import User

def home(request):
    """
    Muestra la página principal con la lista de todos los usuarios ordenados por fecha de creación.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el template home.html y la lista de usuarios.
    """
    users = User.objects.all().order_by('-created_at')
    return render(request, 'migrationsdb/home.html', {'users': users})

def create_user(request):
    """
    Maneja la creación de un nuevo usuario. Muestra el formulario en GET y procesa los datos en POST.
    :param request: El objeto HttpRequest de Django.
    :return: HttpResponse con el formulario de usuario o redirección al home tras creación exitosa.
    """
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('home')
        return render(request, 'migrationsdb/user_form.html', {'form': form})

    form = UserForm()
    return render(request, 'migrationsdb/user_form.html', {'form': form})

def update_user(request, user_id):
    """
    Maneja la actualización de un usuario existente. Busca el usuario por ID y permite editarlo.
    :param request: El objeto HttpRequest de Django.
    :param user_id: ID del usuario a actualizar.
    :return: HttpResponse con el formulario de edición o redirección al home tras actualización exitosa.
    """
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('home')
        return render(request, 'migrationsdb/user_form.html', {'form': form, 'user': user})

    form = UserForm(instance=user)
    return render(request, 'migrationsdb/user_form.html', {'form': form, 'user': user})

def delete_user(request, user_id):
    """
    Elimina un usuario específico de la base de datos y redirige al home.
    :param request: El objeto HttpRequest de Django.
    :param user_id: ID del usuario a eliminar.
    :return: HttpResponse que redirige al home con mensaje de confirmación.
    """
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'Usuario eliminado exitosamente.')
    return redirect('home')