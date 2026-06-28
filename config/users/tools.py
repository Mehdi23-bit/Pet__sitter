import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings


def generate_otp(email):
    otp = str(random.randint(100000, 999999))
    cache.set(f"otp:{email}", otp, timeout=settings.OTP_EXPIRY_SECONDS)
    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP code is: {otp}\nExpires in 5 minutes.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )
    return otp


def verify_otp(email, otp):
    cached_otp = cache.get(f"otp:{email}")
    if cached_otp is None:
        return None, "OTP expired."
    if cached_otp != otp:
        return None, "Invalid OTP."
    return True, "OTP verified."


def delete_otp(email):
    cache.delete(f"otp:{email}")
    
    
def check_otp(email):
    return cache.get(f"otp:{email}") 