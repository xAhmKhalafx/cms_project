from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Assignment
from .forms import AssignmentForm

def is_admin(user):
    return user.is_staff

def is_lecturer(user):
    return hasattr(user, "lecturer_profile")

def owns_assignment(user, assignment: Assignment):
    return is_lecturer(user) and assignment.course.lecturer_id == user.lecturer_profile.pk

@login_required
def assignments_list(request):
    if not (is_admin(request.user) or is_lecturer(request.user)):
        return redirect("dashboard")
    qs = Assignment.objects.select_related("course").order_by("-posted_at")
    if is_lecturer(request.user) and not is_admin(request.user):
        qs = qs.filter(course__lecturer=request.user.lecturer_profile)
    return render(request, "console/assignments_list.html", {"assignments": qs, "is_admin": is_admin(request.user)})

@login_required
def assignments_create(request):
    if not (is_admin(request.user) or is_lecturer(request.user)):
        return redirect("dashboard")
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            # lecturers can only create under their own course
            if is_lecturer(request.user) and not is_admin(request.user):
                if a.course.lecturer_id != request.user.lecturer_profile.pk:
                    messages.error(request, "You can only create assignments for your own courses.")
                    return redirect("console-assignments-list")
            a.save()
            messages.success(request, "Assignment created.")
            return redirect("console-assignments-list")
    else:
        form = AssignmentForm()
    return render(request, "console/assignments_form.html", {"form": form, "title": "Create Assignment"})

@login_required
def assignments_edit(request, assignment_id):
    a = get_object_or_404(Assignment, pk=assignment_id)
    if not (is_admin(request.user) or owns_assignment(request.user, a)):
        messages.error(request, "You don't have permission to edit this assignment.")
        return redirect("console-assignments-list")
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=a)
        if form.is_valid():
            # same guard on course change
            new = form.save(commit=False)
            if is_lecturer(request.user) and not is_admin(request.user):
                if new.course.lecturer_id != request.user.lecturer_profile.pk:
                    messages.error(request, "You can only assign to your own courses.")
                    return redirect("console-assignments-list")
            new.save()
            messages.success(request, "Assignment updated.")
            return redirect("console-assignments-list")
    else:
        form = AssignmentForm(instance=a)
    return render(request, "console/assignments_form.html", {"form": form, "title": "Edit Assignment"})

@login_required
def assignments_delete(request, assignment_id):
    a = get_object_or_404(Assignment, pk=assignment_id)
    if not (is_admin(request.user) or owns_assignment(request.user, a)):
        messages.error(request, "You don't have permission to delete this assignment.")
        return redirect("console-assignments-list")
    if request.method == "POST":
        a.delete()
        messages.success(request, "Assignment deleted.")
        return redirect("console-assignments-list")
    return render(request, "console/confirm_delete.html", {"what": f"Assignment {a.title}"})
