# contact/views.py

from rest_framework import viewsets, status
from rest_framework.views import APIView
from .models import Reservation, Message, Review
from .serializers import ReservationSerializer, TreatingReservationSerializer, MessageSerializer, ReviewSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Q
from django.contrib.auth import get_user_model


# loading the User model
User = get_user_model()


class ReservationView(viewsets.ModelViewSet):
    """
    GET  /reservations/ -> return the reservations related to the logged-in user
                            (either as the owner who booked, or the sitter who was booked)
    POST /reservations/ -> create a new reservation with a sitter

    Only used by authenticated users; access is scoped to the requesting
    user via get_queryset(), not just enforced by permission_classes.
    """
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # This method serves the GET requests (list/retrieve).
        user = self.request.user
        # Return only reservations where the user is involved,
        # whether as the sitter or as the owner.
        return Reservation.objects.filter(Q(sitter=user) | Q(owner=user)).distinct()

    def perform_create(self, serializer):
        # This method serves POST requests (create).
        # The owner is always the authenticated user making the request -
        # never trust an "owner" field from the client for this.
        serializer.save(owner=self.request.user)


class ReservationHandlingView(APIView):
    """
    GET   /contact/status/<int:reservation_id>/ -> return the status of a reservation
    PATCH /contact/status/<int:reservation_id>/ -> modify the status of a reservation
                                                          (must be the sitter responsible for it)

    GET requires the requester to be either the owner or the sitter on the
    reservation. PATCH requires the requester to specifically be the sitter,
    and only allows transitions defined in VALID_TRANSITIONS below.
    """
    permission_classes = [permissions.IsAuthenticated]

    # Rules for which status changes are allowed, and from which starting status.
    VALID_TRANSITIONS = {
        "pending": {"accepted", "rejected"},
        "accepted": {"confirmed"},
        "confirmed": {"finished"},
    }

    def get(self, request, reservation_id):
        # This method handles GET requests: return the current status only,
        # and only to a user who is actually part of this reservation
        # (previously this looked up the reservation by pk alone, which let
        # any authenticated user check the status of any reservation).
        user = request.user
        try:
            reservation = Reservation.objects.get(
                Q(pk=reservation_id) & (Q(sitter=user) | Q(owner=user))
            )
        except Reservation.DoesNotExist:
            return Response(
                {"error": "Reservation not found or you don't have access to it."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response({"status": reservation.status}, status=status.HTTP_200_OK)

    def patch(self, request, reservation_id):
        # This method handles PATCH requests: update the reservation's status.
        # Load and validate the incoming data first.
        serializer = TreatingReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]
        user = request.user

        # Only the sitter responsible for this reservation may change its status.
        # Wrapped in try/except to avoid crashing on a missing/foreign reservation.
        try:
            reservation = Reservation.objects.get(pk=reservation_id, sitter=user)
        except Reservation.DoesNotExist:
            return Response(
                {"error": "Reservation not found or you don't have access to it."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check whether the requested transition is allowed from the current status.
        allowed = self.VALID_TRANSITIONS.get(reservation.status, set())
        if new_status not in allowed:
            return Response(
                {"error": f"Cannot change status from '{reservation.status}' to '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Apply and persist the new status.
        reservation.status = new_status
        reservation.save()
        return Response({"message": "Reservation status updated successfully."}, status=status.HTTP_200_OK)


class MessageView(viewsets.ModelViewSet):
    """
    GET  /message/<int:other_user_id>/ -> return the messages exchanged with a specific user
    POST /message/<int:other_user_id>/ -> send a message to a specific user

    Used only by authenticated users.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # This method serves GET requests.
        other_user_id = self.kwargs["other_user_id"]
        user = self.request.user
        # Look up the other user, guarding against a nonexistent id.
        try:
            other_user = User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            raise NotFound("The other user does not exist.")
        # Return only messages exchanged between these two specific users.
        return Message.objects.filter(
            Q(receiver=other_user, sender=user) | Q(receiver=user, sender=other_user)
        )

    def perform_create(self, serializer):
        # This method serves POST requests.
        other_user_id = self.kwargs["other_user_id"]
        try:
            other_user = User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            raise NotFound("Receiver doesn't exist.")
        # Sender is always the authenticated user; receiver comes from the URL.
        serializer.save(sender=self.request.user, receiver=other_user)


class ReviewView(viewsets.ModelViewSet):
    """
    GET  /review/<int:reservation_id>/ -> return the reviews for a reservation (public/shared -
                                           no ownership filter, anyone authenticated can view them)
    POST /review/<int:reservation_id>/ -> create a review for a finished reservation
                                           (only the owner of that reservation may leave one)

    Reviews are intentionally shared/public once created - viewing them is
    not restricted to the two parties involved in the reservation.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # This method handles GET requests.
        # Reviews are public/shared by design, so no owner/sitter filter here.
        reservation_id = self.kwargs["reservation_id"]
        return Review.objects.filter(reservation_id=reservation_id)

    def perform_create(self, serializer):
        # This method handles POST requests.
        reservation_id = self.kwargs["reservation_id"]
        # Only the owner of the reservation may leave a review for it.
        try:
            reservation = Reservation.objects.get(pk=reservation_id, owner=self.request.user)
        except Reservation.DoesNotExist:
            raise PermissionDenied("This reservation isn't yours.")
        # Reviews can only be left once the reservation is finished.
        if reservation.status != "finished":
            raise PermissionDenied("You can only rate finished reservations.")
        # Prevent duplicate reviews for the same reservation.
        # NOTE: this check-then-create is not atomic - a race between two
        # near-simultaneous requests could still create two reviews. The
        # reliable fix is a OneToOneField (or unique=True) on Review.reservation
        # at the model level, so the database itself enforces uniqueness.
        if Review.objects.filter(reservation_id=reservation_id).exists():
            raise PermissionDenied("This reservation has already been reviewed.")
        serializer.save(reservation_id=reservation_id)
