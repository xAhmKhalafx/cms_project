from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_id", "title", "semester", "lecturer")
    list_filter = ("semester",)
    search_fields = ("title",)
