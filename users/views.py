# users/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserCreateSerializer, StudentSerializer, LecturerSerializer
from .models import Student, Lecturer
from django.http import HttpResponse  # add this import if not present

def landing_page(request):
    return HttpResponse("University CMS is running ✅")

@api_view(["GET"])
def me(request):
    """Return basic info about the current user (if logged in)."""
    if request.user.is_authenticated:
        return Response(UserSerializer(request.user).data)
    return Response({"detail": "Not authenticated"}, status=401)

@api_view(["GET"])
def list_students(request):
    qs = Student.objects.select_related("user").all()
    data = StudentSerializer(qs, many=True).data
    return Response(data)

@api_view(["GET"])
def list_lecturers(request):
    qs = Lecturer.objects.select_related("user").all()
    data = LecturerSerializer(qs, many=True).data
    return Response(data)

@api_view(["POST"])
def create_user(request):
    """Optional helper for testing; remove if you don't need it."""
    ser = UserCreateSerializer(data=request.data)
    if ser.is_valid():
        user = ser.save()
        return Response(UserSerializer(user).data, status=201)
    return Response(ser.errors, status=400)
