from rest_framework import viewsets
from .models import ContactRequest
from .serializers import ContactRequestSerializer
from rest_framework import permissions

class ContactRequestView(viewsets.ModelViewSet):
    queryset = ContactRequest.objects.all()
    serializer_class = ContactRequestSerializer
    permission_classes = [permissions.IsAuthenticated]



    

