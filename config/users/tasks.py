from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

@shared_task    
def send_email(subject=None,message=None,from_email=settings.EMAIL_HOST_USER,recipient_list=[]):
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
    )

