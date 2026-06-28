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

class PetOwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Owner: {self.user.email}"


class PetSitterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sitter_profile')
    cin = models.CharField(max_length=20, unique=True)
    cin_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    accepts_dogs = models.BooleanField(default=True)
    accepts_cats = models.BooleanField(default=True)
    accepts_other = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return f"Sitter: {self.user.email} | CIN verified: {self.cin_verified}"
