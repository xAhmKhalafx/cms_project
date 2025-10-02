from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("assignment_id", "title", "course", "due_date", "posted_at")
    search_fields = ("title",)
    list_filter = ("course", "due_date")
