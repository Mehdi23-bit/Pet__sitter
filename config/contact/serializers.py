from rest_framework import serializers
from .models import ContactRequest, Message , Review



class ContactRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = '__all__'
        read_only_fields = ['owner','status', 'created_at']
        


class TreatingRequestSerializer(serializers.Serializer):
    request_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['rejected','accepted','finished'])



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sender','request','created_at']



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['created_at','request']
