from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, VerifyOTPSerializer, SendOTPSerializer , ForgotPasswordSerializer , ResetPasswordSerializer, ModifyPasswordSerializer, PetOwnerSerializer

from  .tools import generate_otp
from rest_framework.views import APIView
from rest_framework.response import Response
from .tools import verify_otp, delete_otp, check_otp, generate_reset_token, verify_reset_token, delete_reset_token
User = get_user_model()


from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Value, FloatField, Case, When
from django.db.models.functions import ACos, Cos, Sin, Radians

from .filters import SitterFilter
from .models import   PetSitterProfile as Sitter
from .serializers import PetSitterSerializer as SitterSerializer  # adjust import path as needed


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        generate_otp(user.email)  # send OTP right after registration




class MeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # always operates on the logged in user
    




class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self,request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data['email']
        
        if not User.objects.filter(email=email).exists():
            return Response({'message':'if this email exists an OTP was sent'},status=200)
        if check_otp(email):
            return Response({'message': 'an otp is already sent, please wait'},status=429)
        else:
            generate_otp(email)
            return Response({'message':'if this email exists an OTP was sent'},status=200)

             
 



class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        success, message = verify_otp(email, otp)

        if not success:
            return Response({'error': message}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': ' =User not found.'}, status=404)

        user.is_active = True
        user.save()
        delete_otp(email)

        return Response({'message': 'Account verified successfully.'}, status=200)    
    
    
    
class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self,request):
        serializer = ForgotPasswordSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']

        if not User.objects.filter(email=email).exists():
            return Response({'message': 'if this email exists Reset Link is sent.'}, status=200)
        generate_reset_token(email)
        return Response({'message': 'if this email exists Reset Link is sent.'}, status=200)
    
    
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self,request):
        serializer =  ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']    
        token = serializer.validated_data['token'] 
        password = serializer.validated_data['password'] 
        
        success,message = verify_reset_token(email,token) 
        
        if not success : 
            return Response({'error' : message},status=400)
        
        delete_reset_token(email)
        
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            return Response({'message': 'password modified successfuly'}, status=200) 
        except User.DoesNotExist:
            return Response({'error': ' =User not found.'}, status=404)
        
           
    
    
class ModifyPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self,request):
        serializer = ModifyPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(email=email)
            if not user.check_password(old_password):
                return Response({'error' : 'old password is not correct '}, status=400)
            user.set_password(new_password)
            user.save()
            return Response({'message': 'password modified successfuly'}, status=200)
        except User.DoesNotExist:
            return Response({'error': ' =User not found.'}, status=404)
    
    
    
    
    
class MePetOwnerView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PetOwnerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.owner_profile    
    
    
    
    
class SitterListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = User.objects.filter(role='sitter').select_related('sitter_profile')

        city = self.request.query_params.get('city')
        species = self.request.query_params.get('species')
        max_price = self.request.query_params.get('max_price')

        if city:
            qs = qs.filter(city__iexact=city)

        if species == 'dog':
            qs = qs.filter(sitter_profile__accepts_dogs=True)
        elif species == 'cat':
            qs = qs.filter(sitter_profile__accepts_cats=True)
        elif species == 'other':
            qs = qs.filter(sitter_profile__accepts_other=True)

        if max_price:
            qs = qs.filter(sitter_profile__price_per_day__lte=max_price)

        return qs.order_by(
            '-sitter_profile__is_premium',
            '-sitter_profile__cin_verified',
            '-sitter_profile__rating',
        )











class SitterSearchView(generics.ListAPIView):
    serializer_class = SitterSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SitterFilter

    def get_queryset(self):
        queryset = Sitter.objects.filter(is_available=True)

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





