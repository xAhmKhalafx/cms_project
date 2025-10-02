from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserBaseForm, UserEditForm, StudentForm, LecturerForm
from .models import Student, Lecturer

def _console_guard(request):
    return request.user.is_staff or hasattr(request.user, "lecturer_profile")

@login_required
def users_list(request):
    if not _console_guard(request):
        return redirect("dashboard")
    # Show both roles (students & lecturers)
    users = User.objects.order_by("username")
    return render(request, "console/users_list.html", {"users": users})

@login_required
def users_create(request):
    if not _console_guard(request):
        return redirect("dashboard")

    if request.method == "POST":
        uform = UserBaseForm(request.POST)
        sform = StudentForm(request.POST, prefix="stu")
        lform = LecturerForm(request.POST, prefix="lec")

        if uform.is_valid():
            role = uform.cleaned_data["role"]
            user = uform.save(commit=False)
            user.set_password(uform.cleaned_data["password"])
            # Let lecturers access console easily
            if role == "lecturer":
                user.is_staff = True
            user.save()

            if role == "student":
                if sform.is_valid():
                    Student.objects.create(
                        user=user,
                        student_number=sform.cleaned_data["student_number"],
                        program=sform.cleaned_data["program"],
                    )
                else:
                    user.delete()
                    messages.error(request, "Student details invalid.")
                    return render(request, "console/users_create.html", {"uform": uform, "sform": sform, "lform": lform})
            else:  # lecturer
                if lform.is_valid():
                    Lecturer.objects.create(
                        user=user,
                        employee_number=lform.cleaned_data["employee_number"],
                        department=lform.cleaned_data["department"],
                    )
                else:
                    user.delete()
                    messages.error(request, "Lecturer details invalid.")
                    return render(request, "console/users_create.html", {"uform": uform, "sform": sform, "lform": lform})

            messages.success(request, "User created.")
            return redirect("console-users-list")
    else:
        uform = UserBaseForm()
        sform = StudentForm(prefix="stu")
        lform = LecturerForm(prefix="lec")

    return render(request, "console/users_create.html", {"uform": uform, "sform": sform, "lform": lform})

@login_required
def users_edit(request, user_id):
    if not _console_guard(request):
        return redirect("dashboard")

    user = get_object_or_404(User, pk=user_id)
    role = "student" if hasattr(user, "student_profile") else "lecturer" if hasattr(user, "lecturer_profile") else "unknown"

    if request.method == "POST":
        uform = UserEditForm(request.POST, instance=user)
        sform = StudentForm(request.POST, prefix="stu", instance=getattr(user, "student_profile", None))
        lform = LecturerForm(request.POST, prefix="lec", instance=getattr(user, "lecturer_profile", None))

        if uform.is_valid() and ((role=="student" and sform.is_valid()) or (role=="lecturer" and lform.is_valid()) or role=="unknown"):
            uform.save()
            if role=="student":
                sform.save()
            elif role=="lecturer":
                lform.save()
            messages.success(request, "User updated.")
            return redirect("console-users-list")
    else:
        uform = UserEditForm(instance=user)
        sform = StudentForm(prefix="stu", instance=getattr(user, "student_profile", None))
        lform = LecturerForm(prefix="lec", instance=getattr(user, "lecturer_profile", None))

    return render(request, "console/users_edit.html", {"uform": uform, "sform": sform, "lform": lform, "user_obj": user, "role": role})

@login_required
def users_delete(request, user_id):
    if not _console_guard(request):
        return redirect("dashboard")
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted.")
        return redirect("console-users-list")
    return render(request, "console/confirm_delete.html", {"what": f"User {user.username}"})
