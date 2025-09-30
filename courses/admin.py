from django.contrib import admin
from .models import Course, Assignment

import csv
from django.http import HttpResponse

def export_assignments_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=assignments.csv'
    writer = csv.writer(response)
    writer.writerow(["course", "title", "due_date"])
    for a in queryset:
        writer.writerow([a.course.title, a.title, a.due_date])
    return response
export_assignments_csv.short_description = "Export selected assignments to CSV"

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("get_pk", "title", "lecturer_display")
    search_fields = ("title",)

    def get_pk(self, obj):
        return obj.pk
    get_pk.short_description = "ID"
    get_pk.admin_order_field = "pk"

    def lecturer_display(self, obj):
        # Works whether your model field is 'lecturer', 'instructor', or 'owner'
        return getattr(obj, "lecturer", None) or getattr(obj, "instructor", None) or getattr(obj, "owner", "")
    lecturer_display.short_description = "Lecturer"

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("get_pk", "title", "course", "due_date")
    list_filter = ("course", "due_date")
    search_fields = ("title", "course__title")

    def get_pk(self, obj):
        return obj.pk
    get_pk.short_description = "ID"
    get_pk.admin_order_field = "pk"
