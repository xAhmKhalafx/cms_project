from django.shortcuts import render, get_object_or_404
from .models import Course

def course_list_page(request):
    courses = Course.objects.select_related("lecturer").all().order_by("title")
    return render(request, "courses/course_list.html", {"courses": courses})

def course_detail_page(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    assignments = course.assignments.all().order_by("-due_date")
    return render(request, "courses/course_detail.html", {"course": course, "assignments": assignments})
