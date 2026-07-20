from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PetOwnerProfile, PetSitterProfile
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'role', 'phone', 'city']


    def create(self, validated_data):
        password = validated_data.pop('password')
        cin = validated_data.pop('cin',None)
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False
        user._cin =  cin
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'city', 'avatar', 'role']
        read_only_fields = ['email', 'role']  # can't change email or role
        
        
        
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)        
    
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()    
    
    
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(min_length=128)
    password = serializers.CharField(min_length=8, write_only=True)   
    
    
    
class ModifyPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8)
    new_password = serializers.CharField(min_length=8)         
    email        = serializers.EmailField()     
    
    
class PetOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetOwnerProfile
        fields = ['user','address']
        read_only_fields = ['user']
        
        
class PetSitterSerializer(serializers.ModelSerializer):
    cin = serializers.CharField(write_only=True)
    class Meta:
        model = PetSitterProfile
        fields = '__all__'
        read_only_fields = ['user']
        
