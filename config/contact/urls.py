from django.urls import path 
from .views import ReservationView, MessageView , ReviewView, ReservationHandlingView

urlpatterns = [
    path('', ReservationView.as_view({
        'get':'list',
        'post':'create'
    }), name="contact_request")
    ,path('<int:pk>/', ReservationView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='contact_detail'),

    path('status/<int:reservation_id>/', ReservationHandlingView.as_view(), name="status"),
   path('message/<int:other_user_id>/' , MessageView.as_view({'get': 'list'
                                                           ,'post': 'create'}), name="message_detail"),
   path('review/<int:reservation_id>/', ReviewView.as_view({'get': 'list','post': 'create'}))


]
