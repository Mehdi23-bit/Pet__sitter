from django.urls import path
from .views import RegisterView, MeView, VerifyOTPView, SendOTPView, ForgotPasswordView, ResetPasswordView ,ModifyPasswordView 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
    path('otp/verify/', VerifyOTPView.as_view(), name="verify_otp"),
    path('otp/send/', SendOTPView.as_view(), name="send_otp"),
    path('password/forget/', ForgotPasswordView.as_view(),name="forget_password"),
    path('password/reset/', ResetPasswordView.as_view(), name='reset_password'),
    path('password/modify/', ModifyPasswordView.as_view(), name='modify_password'),
]
