from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import Assignment
from .forms import AssignmentForm


def _console_guard(request):
    # Staff OR any user who has a lecturer profile can use the console
    return request.user.is_staff or hasattr(request.user, "lecturer_profile")


@login_required
def assignments_list(request):
    if not _console_guard(request):
        return redirect("dashboard")
    qs = Assignment.objects.select_related("course").order_by("-posted_at")
    return render(request, "console/assignments_list.html", {"assignments": qs})


@login_required
def assignments_create(request):
    if not _console_guard(request):
        return redirect("dashboard")
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment created.")
            return redirect("console-assignments-list")
    else:
        form = AssignmentForm()
    return render(request, "console/assignments_form.html", {"form": form, "title": "Create Assignment"})


@login_required
def assignments_edit(request, assignment_id):
    if not _console_guard(request):
        return redirect("dashboard")
    a = get_object_or_404(Assignment, pk=assignment_id)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated.")
            return redirect("console-assignments-list")
    else:
        form = AssignmentForm(instance=a)
    return render(request, "console/assignments_form.html", {"form": form, "title": "Edit Assignment"})


@login_required
def assignments_delete(request, assignment_id):
    if not _console_guard(request):
        return redirect("dashboard")
    a = get_object_or_404(Assignment, pk=assignment_id)
    if request.method == "POST":
        a.delete()
        messages.success(request, "Assignment deleted.")
        return redirect("console-assignments-list")
    return render(request, "console/confirm_delete.html", {"what": f"Assignment {a.title}"})
