from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Enrollment
from .forms import CourseForm
from users.models import Student


def is_admin(user):
    return user.is_staff

def is_lecturer(user):
    return hasattr(user, "lecturer_profile")

def can_edit_course(user, course: Course):
    return is_admin(user) or (is_lecturer(user) and course.lecturer_id == user.lecturer_profile.pk)

@login_required
def courses_manage_list(request):
    if not (is_admin(request.user) or is_lecturer(request.user)):
        return redirect("dashboard")
    # Lecturers see only their courses; Admin sees all
    qs = Course.objects.select_related("lecturer__user").order_by("title")
    if is_lecturer(request.user) and not is_admin(request.user):
        qs = qs.filter(lecturer=request.user.lecturer_profile)
    return render(request, "console/courses_list.html", {"courses": qs, "is_admin": is_admin(request.user)})

@login_required
def courses_create(request):
    # Only Admin creates courses (lecturers cannot create random courses)
    if not is_admin(request.user):
        messages.error(request, "Only admins can create courses.")
        return redirect("console-courses-list")
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
    course = get_object_or_404(Course, pk=course_id)
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to edit this course.")
        return redirect("console-courses-list")
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
    course = get_object_or_404(Course, pk=course_id)
    if not is_admin(request.user):  # delete is admin-only
        messages.error(request, "Only admins can delete courses.")
        return redirect("console-courses-list")
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted.")
        return redirect("console-courses-list")
    return render(request, "console/confirm_delete.html", {"what": f"Course {course.title}"})

@login_required
def course_enrollments(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not can_edit_course(request.user, course):  # same helper as above
        messages.error(request, "You don't have permission to manage enrollments for this course.")
        return redirect("console-courses-list")

    # enrolled + available students
    enrolled = Enrollment.objects.select_related("student__user").filter(course=course)
    enrolled_ids = [e.student_id for e in enrolled]
    available_students = Student.objects.select_related("user").exclude(pk__in=enrolled_ids)

    return render(request, "console/course_enrollments.html", {
        "course": course,
        "enrolled": enrolled,
        "available_students": available_students
    })

@login_required
def toggle_enrollment(request, course_id, student_id):
    course = get_object_or_404(Course, pk=course_id)
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to change enrollments for this course.")
        return redirect("console-courses-list")
    student = get_object_or_404(Student, pk=student_id)

    existing = Enrollment.objects.filter(course=course, student=student).first()
    if existing:
        existing.delete()
        messages.info(request, f"Removed {student} from {course}.")
    else:
        Enrollment.objects.create(course=course, student=student)
        messages.success(request, f"Enrolled {student} to {course}.")
    return redirect("console-course-enrollments", course_id=course.course_id)