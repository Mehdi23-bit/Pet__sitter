from rest_framework import serializers
from .models import Pet


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = [
            'id', 'name', 'species', 'breed',
            'age', 'weight_kg', 'notes', 'photo', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']