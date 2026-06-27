from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER  = 'owner', 'Pet Owner'
        SITTER = 'sitter', 'Pet Sitter'
        ADMIN  = 'admin', 'Admin'
 
    email    = models.EmailField(unique=True)
    phone    = models.CharField(max_length=20, blank=True)
    role     = models.CharField(max_length=10, choices=Role.choices)
    avatar   = models.ImageField(upload_to='avatars/', blank=True,null=True)
    city     = models.CharField(max_length=100, blank=True)
    verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','role']

    def __str__(self):
        return f"User({self.email},{self.role})" 

# Create your models here.
