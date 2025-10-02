from django.shortcuts import render, get_object_or_404
from .models import Course
from submissions.models import Submission


def course_list_page(request):
    courses = Course.objects.select_related("lecturer").all().order_by("title")
    return render(request, "courses/course_list.html", {"courses": courses})

def course_detail_page(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    assignments = course.assignments.all().order_by("-due_date")

    my_submissions = {}
    if request.user.is_authenticated and hasattr(request.user, "student_profile"):
        subs = Submission.objects.filter(
            student=request.user.student_profile,
            assignment__in=assignments
        ).select_related("assignment")
        my_submissions = {s.assignment_id: s for s in subs}

    return render(request, "courses/course_detail.html", {
        "course": course,
        "assignments": assignments,
        "my_submissions": my_submissions,
    })