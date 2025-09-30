from django.urls import path
from .views import UserListCreateAPIView

urlpatterns = [
    path('', UserListCreateAPIView.as_view(), name='user-list-create'),
]