from rest_framework import serializers
from .models import Reservation , Message , Review



class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ['owner','status', 'created_at']
        


class TreatingReservationSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['rejected','accepted','finished'])



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sender','receiver','created_at']

        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['created_at','reservation']
