from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from assignments.models import Assignment
from users.models import Student
from .models import Submission
from .forms import SubmissionForm

@login_required
def submit_assignment_page(request, assignment_id):
    if not hasattr(request.user, "student_profile"):
        messages.error(request, "Only students can submit assignments.")
        return redirect("course-list-page")

    assignment = get_object_or_404(Assignment, pk=assignment_id)
    student = request.user.student_profile

    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            Submission.objects.update_or_create(
                assignment=assignment, student=student,
                defaults={"file": form.cleaned_data["file"]}
            )
            messages.success(request, "Submission uploaded.")
            return redirect("course-detail-page", course_id=assignment.course_id)
    else:
        form = SubmissionForm()

    return render(request, "submissions/submission_form.html", {"form": form, "assignment": assignment})

@login_required
def list_submissions_page(request, assignment_id):
    if not hasattr(request.user, "lecturer_profile"):
        messages.error(request, "Only lecturers can view submissions.")
        return redirect("course-list-page")

    assignment = get_object_or_404(Assignment, pk=assignment_id)
    subs = assignment.submissions.select_related("student__user").all().order_by("-submitted_at")
    return render(request, "submissions/submission_list.html", {"assignment": assignment, "submissions": subs})

@login_required
def grade_submission_page(request, submission_id):
    if not hasattr(request.user, "lecturer_profile"):
        messages.error(request, "Only lecturers can grade.")
        return redirect("course-list-page")

    submission = get_object_or_404(Submission, pk=submission_id)
    if request.method == "POST":
        submission.grade = float(request.POST.get("grade"))
        submission.feedback = request.POST.get("feedback", "")
        submission.save()
        messages.success(request, "Grade saved.")
        return redirect("submissions-list-page", assignment_id=submission.assignment_id)

    return render(request, "submissions/grade_form.html", {"submission": submission})
