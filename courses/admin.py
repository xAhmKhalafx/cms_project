from django.contrib import admin
from .models import Course, Assignment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_id", "title", "semester")
    list_filter = ("semester",)
    search_fields = ("title",)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("assignment_id", "title", "course", "due_date", "posted_at")
    list_filter = ("course", "due_date")
    search_fields = ("title",)
