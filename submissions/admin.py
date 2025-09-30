from django.contrib import admin
from .models import Submission

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("submission_id", "assignment", "student", "grade", "submitted_at")
    list_filter = ("assignment", "grade")
    search_fields = ("assignment__title", "student__user__username")
