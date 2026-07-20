from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Reservation, Message, Review  
from .serializers import ReservationSerializer, TreatingReservationSerializer , MessageSerializer, ReviewSerializer
from rest_framework import permissions
from rest_framework.response import Response 
from rest_framework.exceptions import PermissionDenied ,NotFound
from django.db.models import Q
from django.conf import settings

class ReservationView(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Reservation.objects.filter(Q(sitter=user) | Q(owner=user)).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ReservationHandlingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TreatingReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation_id = serializer.validated_data["reservation_id"]
        status = serializer.validated_data["status"]
        user = request.user
        try:
            reservation = Reservation.objects.get(pk=reservation_id,sitter=user)
        except Reservation.DoesNotExist:
            return Response({"error": "there was an error when you wanna access that request"},status=404)
        reservation.status = status
        reservation.save()
        return Response({"message": "reservation status changed successfuly"}, status=200)


class MessageView(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        receiver_id = self.kwargs["receiver_id"]
        user = self.request.user 
        try:
            receiver = settings.AUTH_USER_MODEL.objects.get(pk=receiver_id)
        except settings.AUTH_USER_MODEL.DoesNotExist:
            raise NotFound("the message is not accessible")    

        return Message.objects.filter(Q(receiver=receiver,sender=user) | Q(receiver=user,sender=receiver))
    
    def perform_create(self,serializer):
        request_id = self.kwargs["request_id"]
        serializer.save(sender=self.request.user,request_id=request_id)


class ReviewView(viewsets.ModelViewSet):                                
    serializer_class = ReviewSerializer                                 
    permission_classes = [permissions.IsAuthenticated]                   
                                                                         
    def get_queryset(self):                                              
        request_id = self.kwargs["request_id"]                           
        return Review.objects.filter(request_id=request_id)             
    def perform_create(self,serializer):                                 
        request_id = self.kwargs["request_id"]
        try:
            request_contact = ContactRequest.objects.get(pk=request_id,owner=self.request.user)
        except ContactRequest.DoesNotExist:   
            raise PermissionDenied("The request is not your")
        
        if request_contact.status !="finished":
            raise PermissionDenied("you can rate only finished tasks")
        
        serializer.save(request_id=request_id)

                                                                         

