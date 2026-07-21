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

   path('change_status/', ReservationHandlingView.as_view(), name="change_status"),
   path('message/<int:request_id>/' , MessageView.as_view({'get': 'list'
                                                           ,'post': 'create'}), name="message"),
   path('review/<int:request_id>/', ReviewView.as_view({'get': 'list','post': 'create'}))


]
