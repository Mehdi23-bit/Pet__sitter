from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import (RegisterSerializer, UserSerializer, VerifyOTPSerializer, 
                          SendOTPSerializer , ForgotPasswordSerializer , 
                          ResetPasswordSerializer, ModifyPasswordSerializer)
from  .tools import generate_otp
from rest_framework.views import APIView
from rest_framework.response import Response
from .tools import (verify_otp, delete_otp, 
                    check_otp, generate_reset_token, 
                    verify_reset_token, delete_reset_token)

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Value, FloatField, Case, When
from django.db.models.functions import ACos, Cos, Sin, Radians

from .filters import SitterFilter
from .models import   SitterProfile as Sitter

from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from .serializers import SitterProfileSerializer as SitterSerializer
from .throttle import IPRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 

import logging


#loading the user model    
User = get_user_model()

#initialization of logger
logger = logging.getLogger(__name__)

class LoginView(TokenObtainPairView):
    throttle_classes = [IPRateThrottle]
    throttle_scope = 'login'
    throttle_rate_limit = 5
    throttle_window = 3600
    permission_classes = [permissions.AllowAny]

class RefreshView(TokenRefreshView):
    throttle_classes = [IPRateThrottle]
    throttle_scope = 'refresh'
    throttle_rate_limit = 5
    throttle_window = 3600
    permission_classes = [permissions.AllowAny]



class RegisterView(generics.CreateAPIView):
    """ 
    Register is class basedView to registration of users.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        try:
            generate_otp(user.email)  # send OTP right after registration
        except Exception as e:
            logger.error(f"error occured in send otp email to used : {user.email}")
       



class MeView(generics.RetrieveUpdateDestroyAPIView):
    """   
     View  for getting data about the logged user.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # always operates on the logged in user
    




class SendOTPView(APIView):
    """ 
     View for sending Otp emails.
    """
    
    throttle_classes = [IPRateThrottle]
    throttle_scope = 'otp_send'
    throttle_rate_limit = 3
    throttle_window = 3600
    permission_classes = [permissions.AllowAny]
    
    def post(self,request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data['email']
        
        if not User.objects.filter(email=email).exists():
            return Response({'message':'if this email exists an OTP was sent'},status=status.HTTP_200_OK)
        if check_otp(email):
            return Response({'message': 'an otp is already sent, please wait'},status=status.HTTP_429_TOO_MANY_REQUESTS)
        else:
            try:
                generate_otp(email)
            except Exception as e:
                logger.error(f"error occured when sending otp to user : {email}.")
                return Response({'error': "otp is not sent ,try again later"},status=status.HTTP_503_SERVICE_UNAVAILABLE)
            return Response({'message':'if this email exists an OTP was sent'},status=status.HTTP_200_OK)

             
 



class VerifyOTPView(APIView):
    
    throttle_classes = [IPRateThrottle]
    throttle_scope = 'verify_otp'
    throttle_rate_limit = 3
    throttle_window = 3600

    """
    View to verify  the otp.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        success, message = verify_otp(email, otp)

        if not success:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save()
        delete_otp(email)

        return Response({'message': 'Account verified successfully.'}, status=status.HTTP_200_OK)    
    
    
    
class ForgotPasswordView(APIView):
    throttle_classes = [IPRateThrottle]
    throttle_scope = 'forgot_pswd'
    throttle_rate_limit = 3
    throttle_window = 3600
    permission_classes = [permissions.AllowAny]
    
    def post(self,request):
        serializer = ForgotPasswordSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']

        if not User.objects.filter(email=email).exists():
            return Response({'message': 'if this email exists Reset Link is sent.'}, status=status.HTTP_200_OK)
        generate_reset_token(email)
        return Response({'message': 'if this email exists Reset Link is sent.'}, status=status.HTTP_200_OK)
    
    
class ResetPasswordView(APIView):
    throttle_classes = [IPRateThrottle]
    throttle_scope = 'reset_pswd'
    throttle_rate_limit = 3
    throttle_window = 3600
    permission_classes = [permissions.AllowAny]
    
    def post(self,request):
        serializer =  ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']    
        token = serializer.validated_data['token'] 
        password = serializer.validated_data['password'] 
        
        success,message = verify_reset_token(email,token) 
        
        if not success : 
            return Response({'error' : message},status=status.HTTP_400_BAD_REQUEST)
        
        delete_reset_token(email)
        
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            return Response({'message': 'password modified successfuly'}, status=status.HTTP_200_OK) 
        except User.DoesNotExist:
            return Response({'error': ' User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
           
    
    
class ModifyPasswordView(APIView):
    """ 
      View for modifying the password.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self,request):
        serializer = ModifyPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user 
        email = user.email 
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password'] 
        if not user.check_password(old_password):
                return Response({'error' : 'old password is not correct '}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'message': 'password modified successfuly'}, status=status.HTTP_200_OK)
    
    
    
class SitterListView(generics.ListAPIView):
    """
      View list sitters.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = User.objects.filter(sitter__isnull=False)

        city = self.request.query_params.get('city')
        species = self.request.query_params.get('species')
        max_price = self.request.query_params.get('max_price')

        if city:
            qs = qs.filter(city__iexact=city)

        if species == 'dog':
            qs = qs.filter(sitter__accepts_dogs=True)
        elif species == 'cat':
            qs = qs.filter(sitter__accepts_cats=True)
        elif species == 'other':
            qs = qs.filter(sitter__accepts_other=True)

        if max_price:
            qs = qs.filter(sitter__price_per_day__lte=max_price)

        return qs.order_by(
            '-sitter__is_premium',
            '-sitter__rating',
        )

class SitterSearchView(generics.ListAPIView):
    """
      View for search sitters with filters.
    """       
    serializer_class = SitterSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SitterFilter

    def get_queryset(self):
        queryset = Sitter.objects
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')

        # --- Quality score: reviews + experience + premium boost + cold-start fairness ---
        queryset = queryset.annotate(
            quality_score=(
                F('rating') * 3.0
                + F('completed_bookings_count') * 0.05
                + Case(
                    When(is_premium=True, then=Value(5.0)),
                    default=Value(0.0),
                    output_field=FloatField(),
                )
                + Case(
                    # give new sitters with few reviews a temporary visibility boost
                    # so they aren't permanently buried under established sitters
                    When(review_count__lt=3, then=Value(2.5)),
                    default=Value(0.0),
                    output_field=FloatField(),
                )
            )
        )

        if lat and lng:
            lat, lng = float(lat), float(lng)
            queryset = queryset.annotate(
                distance_km=6371 * ACos(
                    Cos(Radians(lat)) * Cos(Radians(F('latitude')))
                    * Cos(Radians(F('longitude')) - Radians(lng))
                    + Sin(Radians(lat)) * Sin(Radians(F('latitude')))
                )
            ).annotate(
                distance_bucket=Case(
                    When(distance_km__lte=5, then=Value(0)),
                    When(distance_km__lte=15, then=Value(1)),
                    When(distance_km__lte=30, then=Value(2)),
                    default=Value(3),
                    output_field=FloatField(),
                )
            ).order_by('distance_bucket', '-quality_score')
        else:
            # no location provided -- fall back to quality-only ranking
            queryset = queryset.order_by('-quality_score')

        return queryset




class IsOwnerOrReadOnly(permissions.BasePermission):
    """
     Permission to check if the user is the owner of the sitter profile or just become readonly.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class SitterProfileView(viewsets.ModelViewSet):
    queryset = Sitter.objects.select_related("user").all()
    serializer_class = SitterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        if Sitter.objects.filter(user=self.request.user).exists():
            raise ValidationError("You already have a sitter profile.")
        serializer.save(user=self.request.user)
