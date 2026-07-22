# pets/views.py
 
from rest_framework import generics, permissions
from .models import Pet
from .serializers import PetSerializer
from users.permissions import IsOwner
 
 
class PetListCreateView(generics.ListCreateAPIView):
    """
    GET  /pets/  -> list all pets belonging to the logged-in user.
    POST /pets/  -> create a new pet, automatically owned by the logged-in user.
 
    Only authenticated users can access this view, and IsOwner is kept here
    as a consistency/defense-in-depth measure even though get_queryset()
    already scopes results to the requesting user.
    """
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
 
    def get_queryset(self):
        # Restrict results to pets owned by the current user only.
        # This also means other users' pets are never listed here,
        # not even by accident.
        return Pet.objects.filter(owner=self.request.user)
 
    def perform_create(self, serializer):
        # Force the owner to be the logged-in user server-side.
        # Never trust an "owner" field from the request body for this -
        # the client should not be able to create a pet on someone else's behalf.
        serializer.save(owner=self.request.user)
 
 
class PetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /pets/<id>/  -> retrieve a single pet (only if owned by the user).
    PATCH  /pets/<id>/  -> partially update a pet (only if owned by the user).
    PUT    /pets/<id>/  -> fully update a pet (only if owned by the user).
    DELETE /pets/<id>/  -> delete a pet (only if owned by the user).
 
    NOTE: make sure PetSerializer marks `owner` as read_only. Otherwise a
    client could PATCH/PUT with a different "owner" id and reassign the pet
    to another user's account. This view does not override perform_update,
    so serializer-level protection is the only thing guarding that field.
    """
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
 
    def get_queryset(self):
        # Pets outside this queryset simply don't exist from this user's
        # point of view (404), rather than existing-but-forbidden (403).
        # This avoids leaking whether a given pet id belongs to someone else.
        return Pet.objects.filter(owner=self.request.user)
 

