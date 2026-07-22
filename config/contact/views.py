from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Reservation, Message, Review
from .serializers import ReservationSerializer, TreatingReservationSerializer, MessageSerializer, ReviewSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


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

    VALID_TRANSITIONS = {
        "pending": {"accepted", "rejected"},
        "accepted": {"finished","confirmed"},
    }

    def post(self, request):
        serializer = TreatingReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation_id = serializer.validated_data["reservation_id"]
        new_status = serializer.validated_data["status"]
        user = request.user

        try:
            reservation = Reservation.objects.get(pk=reservation_id, sitter=user)
        except Reservation.DoesNotExist:
            return Response({"error": "Reservation not found or you don't have access to it."}, status=status.HTTP_404_NOT_FOUND)

        allowed = self.VALID_TRANSITIONS.get(reservation.status, set())
        if new_status not in allowed:
            return Response(
                {"error": f"Cannot change status from '{reservation.status}' to '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = new_status
        reservation.save()
        return Response({"message": "Reservation status updated successfully."}, status=status.HTTP_200_OK)


class MessageView(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        other_user_id = self.kwargs["other_user_id"]
        user = self.request.user
        try:
            other_user = User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            raise NotFound("The other user does not exist.")
        return Message.objects.filter(
            Q(receiver=other_user, sender=user) | Q(receiver=user, sender=other_user)
        )

    def perform_create(self, serializer):
        other_user_id = self.kwargs["other_user_id"]
        try:
            other_user = User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            raise NotFound("Receiver doesn't exist.")
        serializer.save(sender=self.request.user, receiver=other_user)


class ReviewView(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        reservation_id = self.kwargs["reservation_id"]
        return Review.objects.filter(reservation_id=reservation_id)

    def perform_create(self, serializer):
        reservation_id = self.kwargs["reservation_id"]
        try:
            reservation = Reservation.objects.get(pk=reservation_id, owner=self.request.user)
        except Reservation.DoesNotExist:
            raise PermissionDenied("This reservation isn't yours.")

        if reservation.status != "finished":
            raise PermissionDenied("You can only rate finished reservations.")

        if Review.objects.filter(reservation_id=reservation_id).exists():
            raise PermissionDenied("This reservation has already been reviewed.")

        serializer.save(reservation_id=reservation_id)
