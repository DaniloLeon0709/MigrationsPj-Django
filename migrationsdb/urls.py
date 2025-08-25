from django.urls import path
from migrationsdb import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_user, name='create_user'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
    ]