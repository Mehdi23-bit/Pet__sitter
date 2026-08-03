import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
import secrets
from .tasks import send_email

def generate_otp(email):

    delete_otp(email)
    otp = str(random.randint(100000, 999999))
    cache.set(f"otp:{email}", otp ,timeout=settings.OTP_EXPIRY_SECONDS)
    cache.set(f"attempts:{email}" , 0 ,timeout=settings.OTP_EXPIRY_SECONDS)
    send_email.delay(
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
    attempts = cache.incr(f"attempts:{email}")    

    if attempts > settings.VERIFY_ATTEMPTS_LIMIT:
        return None , "you've hit the limit of attempts of verifying , try again later"
    if cached_otp != otp:
        return None, "Invalid OTP."
    
        
    return True, "OTP verified."


def delete_otp(email):
    cache.delete(f"otp:{email}")
    cache.delete(f"attempts:{email}")
    
def check_otp(email):
    return cache.get(f"otp:{email}") 



def generate_reset_token(email):
    token = secrets.token_urlsafe(128)
    cache.set(f"reset_token:{email}", token, timeout=settings.TOKEN_EXPIRY_SECONDS )
    send_email.delay(
        subject="Your Reset Link",
        message=f"Your Reset Link is: {settings.FRONTEND_URL}/reset-password?email={email}&token={token}\nExpires in 5 minutes.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )
    return token

def verify_reset_token(email,token):
    cached_token = cache.get(f"reset_token:{email}")
    if cached_token is None:
        return None, "Token expired."
    if cached_token != token:
        return None, "Invalid Token."
    return True, "Verified Token"

def delete_reset_token(email):
    cache.delete(f"reset_token:{email}")


def get_client_ip(request):
    ip = request.META.get('HTTP_X_CLIENT_IP')
    if ip :
        return ip 
    return request.META.get('REMOTE_ADDR')
