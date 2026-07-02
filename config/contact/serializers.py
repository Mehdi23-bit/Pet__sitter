from rest_framework import serializers
from .models import ContactRequest



class ContactRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = '__all__'
        read_only_fields = ['owner','status', 'created_at']
        


class TreatingRequestSerializer(serializers.Serializer)
    request_id = serializers.IntegerField()
    status = serializers.choiceField(choices=['rejected','accepted'])
    
                                          
