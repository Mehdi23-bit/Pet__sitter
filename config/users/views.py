from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, VerifyOTPSerializer, SendOTPSerializer , ForgotPasswordSerializer , ResetPasswordSerializer
from  .tools import generate_otp
from rest_framework.views import APIView
from rest_framework.response import Response
from .tools import verify_otp, delete_otp, check_otp, generate_reset_token, verify_reset_token, delete_reset_token
User = get_user_model()


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
        except User.DoesNotExist:
            return Response({'error': ' =User not found.'}, status=404)
        
        user.set_password(password)
        user.save()
        return Response({'message': 'password modified successfuly'}, status=200)    
    