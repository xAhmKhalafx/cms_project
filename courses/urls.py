from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.list_courses, name='course-list'),
    path('courses/<int:course_id>/assignments/', views.list_course_assignments, name='course-assignments'),
    path('courses/<int:course_id>/assignments/create/', views.create_assignment, name='assignment-create'),
]
