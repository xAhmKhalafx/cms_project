from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from users.models import Lecturer
from .models import Course
from .forms import CourseForm

def _console_guard(request):
    return request.user.is_staff or hasattr(request.user, "lecturer_profile")

@login_required
def courses_manage_list(request):
    if not _console_guard(request):
        return redirect("dashboard")
    courses = Course.objects.select_related("lecturer__user").order_by("title")
    return render(request, "console/courses_list.html", {"courses": courses})

@login_required
def courses_create(request):
    if not _console_guard(request):
        return redirect("dashboard")
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created.")
            return redirect("console-courses-list")
    else:
        form = CourseForm()
    return render(request, "console/courses_form.html", {"form": form, "title": "Create Course"})

@login_required
def courses_edit(request, course_id):
    if not _console_guard(request):
        return redirect("dashboard")
    course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated.")
            return redirect("console-courses-list")
    else:
        form = CourseForm(instance=course)
    return render(request, "console/courses_form.html", {"form": form, "title": "Edit Course"})

@login_required
def courses_delete(request, course_id):
    if not _console_guard(request):
        return redirect("dashboard")
    course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("console-courses-list")
    return render(request, "console/confirm_delete.html", {"what": f"Course {course.title}"})
