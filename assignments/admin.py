from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("assignment_id", "title", "course", "due_date", "posted_at")
    list_filter = ("course", "due_date")
    search_fields = ("title",)
