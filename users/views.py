# users/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserCreateSerializer, StudentSerializer, LecturerSerializer
from .models import Student, Lecturer
from django.http import HttpResponse  # add this import if not present
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
# users/views.py
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_page(request):
    # You can pass real data later; this is a working stub.
    return render(request, "users/dashboard.html", {"username": request.user.username})

def signup_page(request):
    """
    Display a signup form and create a new Django auth user.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # creates new auth.User
            messages.success(request, "Account created! You can log in now.")
            return redirect("login")  # or redirect("landing") if you prefer
    else:
        form = UserCreationForm()
    return render(request, "users/signup.html", {"form": form})


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
