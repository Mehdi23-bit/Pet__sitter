"""
obsolete file not used anymore.
# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PetOwnerProfile, PetSitterProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.role == 'owner':
        PetOwnerProfile.objects.create(user=instance)
    elif instance.role == 'sitter':
        cin = getattr(instance,'cin','')
        PetSitterProfile.objects.create(user=instance, cin=cin)

"""        
