from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from courses.models import Course
from .forms import AssignmentForm

@login_required
def create_assignment_page(request, course_id):
    if not hasattr(request.user, "lecturer_profile"):
        messages.error(request, "Only lecturers can create assignments.")
        return redirect("course-detail-page", course_id=course_id)

    course = get_object_or_404(Course, pk=course_id)
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment created.")
            return redirect("course-detail-page", course_id=course_id)
    else:
        form = AssignmentForm(initial={"course": course})

    return render(request, "assignments/assignment_form.html", {"form": form, "course": course})
