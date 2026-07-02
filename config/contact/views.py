from rest_framework import viewsets
from rest_framework.views import APIView
from .models import ContactRequest, Message  
from .serializers import ContactRequestSerializer, TreatingRequestSerializer , MessageSerializer
from rest_framework import permissions
from rest_framework.response import Response 

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


class ContactRequestHandlingView(APIView)
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
        return Message.objects.filter(request_id=request_id)
    def perform_create(self,serializer):
        request_id = self.kwargs["request_id"]
        serializer.save(sender=self.request.user,request_id=request_id)



