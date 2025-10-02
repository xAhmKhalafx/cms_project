from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from courses.models import Course
from assignments.models import Assignment
from submissions.models import Submission


def user_login(request):
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect("dashboard")
        return render(request, "users/login.html", {"error": "Invalid credentials"})
    return render(request, "users/login.html")

def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    # Simple role check
    role = "student" if hasattr(request.user, "student_profile") else "lecturer" if hasattr(request.user, "lecturer_profile") else "admin" if request.user.is_staff else "guest"
    return render(request, "users/dashboard.html", {"role": role})

def console_home(request):
    # Only staff or lecturers may access
    if not (request.user.is_staff or hasattr(request.user, "lecturer_profile")):
        return redirect("dashboard")

    stats = {
        "courses": Course.objects.count(),
        "assignments": Assignment.objects.count(),
        "submissions": Submission.objects.count(),
    }
    recent_assignments = Assignment.objects.select_related("course").order_by("-posted_at")[:6]
    recent_subs = Submission.objects.select_related("assignment", "student__user").order_by("-submitted_at")[:6]

    return render(request, "console/home.html", {
        "stats": stats,
        "recent_assignments": recent_assignments,
        "recent_submissions": recent_subs
    })