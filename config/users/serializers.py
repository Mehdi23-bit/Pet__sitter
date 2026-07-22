from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import  SitterProfile, SitterPhoto

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email','password']


    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.username = user.email
        user.is_active = False
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']
        read_only_fields = ['email']  # can't change email or role
        
        
        
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
    
    
        
        




class SitterPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model            = SitterPhoto
        fields           = ["id", "photo", "upload_at"]
        read_only_fields = ["id", "upload_at"]


class SitterProfileSerializer(serializers.ModelSerializer):
    photos = SitterPhotoSerializer(source="sitterphoto_set", many=True, read_only=True)
    email  = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model  = SitterProfile
        fields = [
            "id", "email", "bio", "price_per_day",
            "accepts_dogs", "accepts_cats", "accepts_other",
            "rating", "is_premium", "latitude", "longitude",
            "review_count", "completed_bookings_count", "city",
            "photos",
        ]
        read_only_fields = ["rating", "is_premium", "review_count", "completed_bookings_count"]        
