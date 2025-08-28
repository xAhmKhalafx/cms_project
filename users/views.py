from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import User
from .serializers import UserSerializer, UserCreateSerializer

class UserListCreateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_deleted=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# -------------------------------
# Landing Page
# -------------------------------
def landing_page(request):
    return render(request, 'users/landing.html')

# -------------------------------
# Signup Page
# -------------------------------
def signup_page(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

# -------------------------------
# Dashboard Page
# -------------------------------
@login_required
def dashboard_page(request):
    user = request.user
    # Role-based dashboard logic
    if user.role == 'ADMIN':
        template = 'users/admin_dashboard.html'
    elif user.role in ['EDITOR', 'AUTHOR']:
        template = 'users/instructor_dashboard.html'
    else:
        template = 'users/student_dashboard.html'
    
    context = {'user': user}
    return render(request, template, context)