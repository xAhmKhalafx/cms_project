# courses/urls.py
from django.urls import path
from .views import CourseListCreateAPI, CourseDetailAPI  # swap for your app if needed

urlpatterns = [
    path('courses/', CourseListCreateAPI.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailAPI.as_view(), name='course-detail'),
]
