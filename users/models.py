# users/models.py
from django.db import models
from django.contrib.auth.models import User  # default auth user

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_number = models.CharField(max_length=20, unique=True)
    program = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.student_number})"

class Lecturer(models.Model):
    lecturer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="lecturer_profile")
    employee_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.employee_number})"
