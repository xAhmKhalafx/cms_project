from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_id", "title", "semester", "lecturer")
    search_fields = ("title",)
    list_filter = ("semester",)
