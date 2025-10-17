from rest_framework import serializers
from migrationsdb.models import Book, Genre

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']

    def validate_name(self, value):
        """Validar que el nombre del género sea único"""
        instance = self.instance
        if Genre.objects.filter(name=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Ya existe un género con este nombre.")
        return value