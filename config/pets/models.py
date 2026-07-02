from django.db import models
from django.conf import settings


class Pet(models.Model):
    class Species(models.TextChoices):
        DOG = 'dog', 'Dog'
        CAT = 'cat', 'Cat'
        OTHER = 'other', 'Other'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=10, choices=Species.choices)
    breed = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField()
    weight_kg = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='pets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.species}) — {self.owner.email}"