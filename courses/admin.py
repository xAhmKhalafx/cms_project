from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_id", "title", "semester", "lecturer")
    search_fields = ("title",)
    list_filter = ("semester",)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("enrollment_id", "student", "course", "enrolled_at")
    search_fields = ("student__user__username", "course__title")
    list_filter = ("course",)