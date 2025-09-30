from django.contrib import admin
from .models import Student, Lecturer

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "user", "student_number", "program")
    search_fields = ("user__username", "student_number")

@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ("lecturer_id", "user", "employee_number", "department")
    search_fields = ("user__username", "employee_number")
