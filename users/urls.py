# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("me/", views.me, name="users-me"),
    path("students/", views.list_students, name="users-students"),
    path("lecturers/", views.list_lecturers, name="users-lecturers"),
    path("create/", views.create_user, name="users-create"),  # optional helper
]
