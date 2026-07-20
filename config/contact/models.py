from django.db import models
from django.conf import settings
from pets.models import Pet


class ContactRequest(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',  'Pending'
        ACCEPTED  = 'accepted', 'Accepted'
        REJECTED  = 'rejected', 'Rejected'
        FINISHED  = 'finished', 'Finished'
        CONFIRMED = 'confirmed', 'Confirmed'

    owner      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests')
    sitter     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests')
    pets       = models.ManyToManyField(Pet, related_name='contact_requests')
    message    = models.TextField(blank=True)
    start_date = models.DateField()
    end_date   = models.DateField()
    status     = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.email} ===> {self.sitter.email} ({self.status})"


class Message(models.Model):
    request    = models.ForeignKey(ContactRequest, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}"
# Create your models here
#
#
class Review(models.Model):
    request    = models.OneToOneField(ContactRequest, on_delete=models.CASCADE, related_name='review')
    rating     = models.PositiveSmallIntegerField()
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.request.sitter.email} — {self.rating}/5"
