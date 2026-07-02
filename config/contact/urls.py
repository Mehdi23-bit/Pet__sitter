from django.urls import path 
from .views import ContactRequestView

urlpatterns = [
    path('', ContactRequestView.as_view({
        'get':'list',
        'post':'create'
    }), name="contact_request")
    ,path('<int:pk>/', ContactRequestView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='contact_detail')
]
