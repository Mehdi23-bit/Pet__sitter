from rest_framework import viewsets
from rest_framework.views import APIView
from .models import ContactRequest, Message, Review  
from .serializers import ContactRequestSerializer, TreatingRequestSerializer , MessageSerializer, ReviewSerializer
from rest_framework import permissions
from rest_framework.response import Response 
from rest_framework.exceptions import PermissionDenied ,NotFound
class ContactRequestView(viewsets.ModelViewSet):
    serializer_class = ContactRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'owner':
                return ContactRequest.objects.filter(owner=user)
        return ContactRequest.objects.filter(sitter=user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ContactRequestHandlingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TreatingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_id = serializer.validated_data["request_id"]
        status = serializer.validated_data["status"]
        user = request.user
        try:
            contact_request = ContactRequest.objects.get(pk=request_id,sitter=user)
        except ContactRequest.DoesNotExist:
            return Response({"error": "there was an error when you wanna access that request"},status=404)
        contact_request.status = status
        contact_request.save()
        return Response({"message": "request status changed successfuly"}, status=200)


class MessageView(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        request_id = self.kwargs["request_id"]
        user = self.request.user 
        try:
            request_contact = ContactRequest.objects.get(pk=request_id)
        except ContactRequest.DoesNotExist:
            raise NotFound("the message is not accessible")    
        if request_contact.owner != user and request_contact.sitter != user:
            raise PermissionDenied("the message is not accessible ")

        return Message.objects.filter(request_id=request_id)
    
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

                                                                         

