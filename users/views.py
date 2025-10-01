from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import View
from django.contrib import messages
from django import forms 
from django.utils import timezone 
from django.db.models import Avg, Sum, Count 
from django.db.transaction import atomic

# Import forms from local apps
# NOTE: Ensure these forms exist in the respective files!
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AdminUserEditForm
from courses.forms import CourseForm, AssignmentForm
from submissions.forms import AssessmentForm

# Import models from local apps
# NOTE: Ensure these models exist in the respective files!
from .models import User
from courses.models import Course, Assignment, Attendance
from submissions.models import Submission


# ====================================================================
# CUSTOM FORMS (Defined here for immediate context in views)
# ====================================================================

class StudentSubmissionForm(forms.ModelForm):
    """Form used by students to submit or update their assignment content."""
    class Meta:
        model = Submission
        # ✅ FIX: Use the correct field name 'file'
        fields = ['file'] 
        widgets = {
            # Since 'file' is a FileField, use FileInput
            'file': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }

class InstructorMailerForm(forms.Form):
    """Form used by instructors to select a course and draft an email."""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Select Course/Unit",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter email subject'})
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'class': 'form-control', 'placeholder': 'Type your message content here...'}),
        label="Message Body"
    )

    def __init__(self, *args, instructor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if instructor:
            # Filter the course list to only show courses taught by this instructor
            self.fields['course'].queryset = Course.objects.filter(lecturer=instructor)
            if not self.fields['course'].queryset.exists():
                self.fields['course'].help_text = "You are not assigned to any courses."
                self.fields['course'].required = False
                self.fields['course'].widget.attrs['disabled'] = True


# ====================================================================
# HELPER FUNCTIONS FOR ROLE-BASED ACCESS
# ====================================================================

def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

def is_instructor(user):
    return user.is_authenticated and user.role == 'Instructor'
    
def is_student(user):
    return user.is_authenticated and user.role == 'Student'

def is_instructor_of_course(user, course_id):
    """Checks if the given user is the lecturer for the specified course."""
    if not user.is_authenticated or user.role != 'Instructor':
        return False
    # Use pk=course_id for primary key lookup
    return Course.objects.filter(pk=course_id, lecturer=user).exists()


# ====================================================================
# LANDING & AUTHENTICATION VIEWS
# ====================================================================

def landing_page(request):
    """Directs authenticated users to dashboard, unauthenticated to the landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'users/landing.html')

class LoginView(View):
    """Handles user login."""
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        
        return render(request, self.template_name, {'form': form})

class SignUpView(View):
    """Handles user sign up."""
    template_name = 'users/signup.html'
    form_class = CustomUserCreationForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            
            # 🟢 CRITICAL FIX 1: Assign the default role 
            # (Assuming 'Student' is the correct database value)
            user.role = 'Student' 
            
            user.save() 
            login(request, user)
            
            # 🛑 CRITICAL FIX 2: Replace user.get_full_name()
            # Concatenate first_name and last_name, or fall back to email.
            if user.first_name and user.last_name:
                display_name = f"{user.first_name} {user.last_name}"
            else:
                display_name = user.email
            
            messages.success(request, f"Welcome, {display_name}! Your account has been created.")
            
            return redirect('dashboard')
        
        return render(request, self.template_name, {'form': form})


# ====================================================================
# DASHBOARD ROUTING
# ====================================================================

@login_required
def dashboard_page(request):
    """Routes the user to the correct dashboard based on their role."""
    user = request.user
    
    # Use .lower() for case-insensitive role checking to prevent fall-through crashes
    user_role = user.role.lower()
    
    if user_role == 'admin':
        total_courses = Course.objects.count()
        # Count non-deleted users for the total user count
        total_users = User.objects.filter(is_deleted=False).count()
        
        context = {
            'user': user,
            'total_courses': total_courses,
            'total_users': total_users,
        }
        return render(request, 'users/admin_dashboard.html', context)
    
    elif user_role == 'instructor':
        # Courses taught by the instructor
        courses = Course.objects.filter(lecturer=user)
        # Submissions for grading in those courses
        submissions_to_grade = Submission.objects.filter(
            assignment__course__in=courses,
            # Assuming 'status' is now correctly 'pending' or similar based on your model
            grade__isnull=True 
        ).select_related('student', 'assignment__course').order_by('submitted_at')
        
        pending_grades = submissions_to_grade.count()
        
        context = {
            'user': user,
            'pending_grades': pending_grades,
            'submissions_to_grade': submissions_to_grade[:5] # Show top 5 recent submissions
        }
        return render(request, 'users/instructor_dashboard.html', context)
        
    elif user_role == 'student':
        # Courses the student is enrolled in
        # Confirmed: This is the correct related_name
        enrolled_courses = user.enrolled_in_courses.all() 
        my_submissions = Submission.objects.filter(student=user, grade__isnull=False)
        
        # Calculate performance stats
        avg_grade = my_submissions.aggregate(Avg('grade'))['grade__avg']
        
        # Calculate overall attendance rate
        # Confirmed: This is the correct field name 'session_date'
        total_sessions = Attendance.objects.filter(course__in=enrolled_courses).values('course', 'session_date').distinct().count() 
        
        present_sessions = Attendance.objects.filter(student=user, status='P').count() 
        attendance_rate = (present_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        context = {
            'user': user,
            'total_courses': enrolled_courses.count(),
            'avg_grade': f"{avg_grade:.2f}" if avg_grade is not None else 'N/A',
            'attendance_rate': f"{attendance_rate:.0f}%",
            'recent_submissions': my_submissions.select_related('assignment').order_by('-submitted_at')[:5],
        }
        return render(request, 'users/student_dashboard.html', context)
        
    # FINAL FALLBACK: If the user role is still invalid/not recognized.
    # We must redirect to a simple, safe page that accepts GET requests 
    # to break the 405 loop. The base 'landing' page is assumed to be safe.
    messages.error(request, f"Your user role ({user.role}) is unauthorized or invalid. Please contact an administrator.")
    return redirect('landing') 

# ====================================================================
# ADMIN MANAGEMENT VIEWS (Crud and Oversight)
# ====================================================================

@user_passes_test(is_admin)
def admin_user_list(request):
    """Admin view to list all non-deleted users."""
    users = User.objects.filter(is_deleted=False).order_by('last_name')
    context = {'users': users, 'page_title': 'User Management'}
    return render(request, 'admin/user_list.html', context)

@user_passes_test(is_admin)
def admin_user_create(request):
    """Admin view to create a new user."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.username} created successfully.")
            return redirect('admin_user_list')
    else:
        form = CustomUserCreationForm()
        
    context = {'form': form, 'page_title': 'Add New User'}
    return render(request, 'admin/user_form.html', context)

@user_passes_test(is_admin)
def admin_user_edit(request, user_id):
    """Admin view to edit existing user details."""
    user_to_edit = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f"User {user_to_edit.username}'s details updated.")
            return redirect('admin_user_list')
    else:
        form = AdminUserEditForm(instance=user_to_edit)
        
    context = {'form': form, 'page_title': f'Edit User: {user_to_edit.get_full_name()}'}
    return render(request, 'admin/user_form.html', context)

@user_passes_test(is_admin)
def admin_course_list(request):
    """Admin view to list all courses."""
    courses = Course.objects.all().order_by('title').select_related('lecturer')
    context = {'courses': courses, 'page_title': 'Course Management'}
    return render(request, 'admin/course_list.html', context)

@user_passes_test(is_admin)
def admin_course_create(request):
    """Admin view to create a new course and manage enrollments."""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, f"Course '{form.cleaned_data['title']}' created successfully.")
                return redirect('admin_course_list')
        except Exception as e:
            messages.error(request, f"Error creating course: {e}")
            
    else:
        form = CourseForm()
        
    context = {'form': form, 'page_title': 'Create New Course'}
    return render(request, 'admin/course_form.html', context)

@user_passes_test(is_admin)
def admin_course_edit(request, course_id):
    """Admin view to edit an existing course and manage enrollments."""
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated successfully.")
            return redirect('admin_course_list')
    else:
        form = CourseForm(instance=course)
        
    context = {'form': form, 'page_title': f'Edit Course: {course.title}'}
    return render(request, 'admin/course_form.html', context)

@user_passes_test(is_admin)
def admin_submission_list(request):
    """Admin view to list all student submissions for global oversight."""
    submissions = Submission.objects.select_related('student', 'assignment', 'assignment__course').order_by('-submitted_at')
    
    context = {
        'submissions': submissions,
        'page_title': 'Submission Review (Admin)'
    }
    return render(request, 'admin/submission_list.html', context)

@user_passes_test(is_admin)
def admin_grade_submission(request, submission_id):
    """Admin view to grade a specific submission."""
    submission = get_object_or_404(Submission, pk=submission_id)

    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            # Update status if a grade is provided
            submission.status = 'graded' if submission.grade is not None else submission.status
            submission.graded_by = request.user
            submission.graded_at = timezone.now()
            submission.save()
            messages.success(request, f"Submission by {submission.student.get_full_name()} graded successfully!")
            return redirect('admin_submission_list')
    else:
        form = AssessmentForm(instance=submission)

    context = {
        'form': form,
        'submission': submission,
        'page_title': 'Grade Submission (Admin)'
    }
    return render(request, 'admin/submission_grade_form.html', context)

@user_passes_test(is_admin)
def admin_attendance(request):
    """Admin view to mark and edit attendance for any course on any date."""
    courses = Course.objects.all().order_by('title')
    selected_course = None
    selected_date = None
    attendance_records = []
    
    # Process form submission for date and course filtering (via GET request)
    if request.GET.get('course_id') and request.GET.get('attendance_date'):
        try:
            course_id = int(request.GET['course_id'])
            date_str = request.GET.get('attendance_date')
            
            selected_course = get_object_or_404(Course, pk=course_id)
            selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            students = selected_course.students.filter(is_deleted=False).order_by('last_name')
            existing_records = Attendance.objects.filter(
                course=selected_course,
                date=selected_date
            ).in_bulk(field_name='student_id')
            
            # Prepare records list: use existing record or create a default 'absent' placeholder
            for student in students:
                record = existing_records.get(student.id)
                if not record:
                    record = Attendance(course=selected_course, student=student, date=selected_date, status='absent') 
                attendance_records.append(record)

        except (ValueError, TypeError):
            messages.error(request, "Invalid course or date selected.")
            return redirect('admin_attendance')

    # Process form submission for saving attendance (via POST request)
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        date_str = request.POST.get('attendance_date')
        
        if course_id and date_str:
            course = get_object_or_404(Course, pk=course_id)
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            with atomic():
                for key, status in request.POST.items():
                    if key.startswith('status_'):
                        student_id = key.split('_')[1]
                        student = get_object_or_404(User, pk=student_id)
                        
                        # Use update_or_create to efficiently save the data
                        Attendance.objects.update_or_create(
                            course=course,
                            student=student,
                            date=date,
                            defaults={'status': status}
                        )
            
            messages.success(request, f"Attendance for {course.title} on {date} saved successfully.")
            # Redirect to the same page with query parameters to retain the view
            return redirect(f"{request.path}?course_id={course_id}&attendance_date={date_str}") 

    context = {
        'courses': courses,
        'selected_course': selected_course,
        'selected_date': selected_date,
        'attendance_records': attendance_records,
        'page_title': 'Attendance Management (Admin)'
    }
    return render(request, 'admin/attendance_list.html', context)


# ====================================================================
# INSTRUCTOR MANAGEMENT VIEWS (Assignments, Grading, Mailer, Reports)
# ====================================================================

@user_passes_test(is_instructor)
def instructor_assignment_list(request):
    """Instructor view to list all assignments for their courses."""
    instructor_courses = Course.objects.filter(lecturer=request.user)
    assignments = Assignment.objects.filter(course__in=instructor_courses).order_by('-due_date').select_related('course')
    
    context = {
        'assignments': assignments,
        'page_title': 'My Assignments'
    }
    return render(request, 'instructor/assignment_list.html', context)

@user_passes_test(is_instructor)
def instructor_assignment_create(request):
    """Instructor view to create a new assignment for one of their courses."""
    if request.method == 'POST':
        # Pass the instructor to the form for course filtering
        form = AssignmentForm(request.POST, instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Assignment '{form.cleaned_data['title']}' created successfully.")
            return redirect('instructor_assignment_list')
    else:
        form = AssignmentForm(instructor=request.user) 
        
    context = {'form': form, 'page_title': 'Create New Assignment'}
    return render(request, 'instructor/assignment_form.html', context)

@user_passes_test(is_instructor)
def instructor_assignment_edit(request, assignment_id):
    """Instructor view to edit an existing assignment (only if they teach the course)."""
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    
    if not is_instructor_of_course(request.user, assignment.course.id):
        messages.error(request, "You do not have permission to edit this assignment.")
        return redirect('instructor_assignment_list')
        
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment, instructor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Assignment '{assignment.title}' updated successfully.")
            return redirect('instructor_assignment_list')
    else:
        form = AssignmentForm(instance=assignment, instructor=request.user)
        
    context = {'form': form, 'page_title': f'Edit Assignment: {assignment.title}'}
    return render(request, 'instructor/assignment_form.html', context)

@user_passes_test(is_instructor)
def instructor_submission_list(request):
    """Instructor view to list all student submissions in their courses that need review."""
    instructor_courses = Course.objects.filter(lecturer=request.user)
    submissions = Submission.objects.filter(
        assignment__course__in=instructor_courses
    ).select_related('student', 'assignment', 'assignment__course').order_by('-submitted_at')
    
    context = {
        'submissions': submissions,
        'page_title': 'Student Submissions for Review'
    }
    return render(request, 'instructor/submission_list.html', context)

@user_passes_test(is_instructor)
def instructor_grade_submission(request, submission_id):
    """Instructor view to grade a specific submission, restricted to their own courses."""
    submission = get_object_or_404(Submission, pk=submission_id)
    
    if not is_instructor_of_course(request.user, submission.assignment.course.id):
        messages.error(request, "You do not have permission to grade this submission.")
        return redirect('instructor_submission_list')

    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.status = 'graded' if submission.grade is not None else submission.status
            submission.graded_by = request.user
            submission.graded_at = timezone.now()
            submission.save()
            messages.success(request, f"Submission by {submission.student.get_full_name()} graded successfully!")
            return redirect('instructor_submission_list')
    else:
        form = AssessmentForm(instance=submission)

    context = {
        'form': form,
        'submission': submission,
        'page_title': 'Grade Submission'
    }
    return render(request, 'instructor/submission_grade_form.html', context)

@user_passes_test(is_instructor)
def instructor_attendance(request):
    """Instructor view to mark attendance for their assigned courses."""
    courses = Course.objects.filter(lecturer=request.user).order_by('title')
    selected_course = None
    selected_date = None
    attendance_records = []
    
    # Process filtering via GET
    if request.GET.get('course_id') and request.GET.get('attendance_date'):
        try:
            course_id = int(request.GET['course_id'])
            date_str = request.GET.get('attendance_date')
            
            # Crucial check: ensure the instructor is the lecturer of the course
            selected_course = get_object_or_404(Course, pk=course_id, lecturer=request.user)
            selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            students = selected_course.students.filter(is_deleted=False).order_by('last_name')
            existing_records = Attendance.objects.filter(
                course=selected_course,
                date=selected_date
            ).in_bulk(field_name='student_id')
            
            for student in students:
                record = existing_records.get(student.id)
                if not record:
                    record = Attendance(course=selected_course, student=student, date=selected_date, status='absent') 
                attendance_records.append(record)

        except (ValueError, TypeError):
            messages.error(request, "Invalid course or date selected.")
            return redirect('instructor_attendance')
        except Course.DoesNotExist:
            messages.error(request, "You are not authorized to manage attendance for that course.")
            return redirect('instructor_attendance')

    # Process saving via POST
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        date_str = request.POST.get('attendance_date')
        
        if course_id and date_str:
            # Re-check authorization before saving
            course = get_object_or_404(Course, pk=course_id, lecturer=request.user) 
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            with atomic():
                for key, status in request.POST.items():
                    if key.startswith('status_'):
                        student_id = key.split('_')[1]
                        student = get_object_or_404(User, pk=student_id)
                        
                        Attendance.objects.update_or_create(
                            course=course,
                            student=student,
                            date=date,
                            defaults={'status': status}
                        )
            
            messages.success(request, f"Attendance for {course.title} on {date} saved successfully.")
            return redirect(f"{request.path}?course_id={course_id}&attendance_date={date_str}") 

    context = {
        'courses': courses,
        'selected_course': selected_course,
        'selected_date': selected_date,
        'attendance_records': attendance_records,
        'page_title': 'Attendance Management'
    }
    return render(request, 'instructor/attendance_list.html', context)

@user_passes_test(is_instructor)
def instructor_mailer(request):
    """Instructor view to send simulated bulk emails to students in their courses."""
    user = request.user
    
    if request.method == 'POST':
        form = InstructorMailerForm(request.POST, instructor=user)
        if form.is_valid():
            course = form.cleaned_data['course']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            
            student_emails = course.students.filter(is_deleted=False, is_active=True).values_list('email', flat=True).distinct()
            recipient_list = list(student_emails)
            
            if recipient_list:
                # --- SIMULATE EMAIL SENDING (Check your console/log) ---
                print("\n--- START EMAIL SIMULATION ---")
                print(f"From: {user.email}")
                print(f"To: {len(recipient_list)} student(s) in {course.title} (Emails: {', '.join(recipient_list[:5])}...)")
                print(f"Subject: {subject}")
                print(f"Body Preview: {body[:100]}...")
                print("--- END EMAIL SIMULATION ---\n")

                messages.success(request, f"Email successfully **simulated** to {len(recipient_list)} students in {course.title}.")
                return redirect('instructor_mailer')
            else:
                messages.warning(request, f"No active students found in {course.title} to send the email to.")
        else:
            messages.error(request, "Error sending email. Please check your form input.")
    else:
        form = InstructorMailerForm(instructor=user)
        
    context = {
        'form': form,
        'page_title': 'Bulk Student Email',
    }
    return render(request, 'instructor/mailer_form.html', context)


@user_passes_test(is_instructor)
def instructor_reports(request):
    """Instructor view to see reports and aggregated statistics for their courses."""
    user = request.user
    
    courses = Course.objects.filter(lecturer=user).prefetch_related('assignment_set', 'students')
    
    report_data = []
    
    for course in courses:
        # Get graded submissions for the course
        course_submissions = Submission.objects.filter(
            assignment__course=course,
            grade__isnull=False
        ).select_related('student', 'assignment')
        
        avg_grade_result = course_submissions.aggregate(Avg('grade'))
        
        report_data.append({
            'course': course,
            'avg_grade': f"{avg_grade_result['grade__avg']:.2f}" if avg_grade_result['grade__avg'] is not None else 'N/A',
            'graded_count': course_submissions.count(),
            'total_students': course.students.count(),
            'submissions': course_submissions.order_by('assignment__due_date', 'student__last_name'),
        })
        
    context = {
        'report_data': report_data,
        'page_title': 'Course Grade Reports',
    }
    return render(request, 'instructor/reports.html', context)


# ====================================================================
# STUDENT VIEWS (Assignments, Submissions, Performance)
# ====================================================================

@user_passes_test(is_student)
def student_assignment_list(request):
    """Student view to list all enrolled assignments and their submission status."""
    user = request.user
    enrolled_courses = user.enrolled_courses.all()
    
    assignments = Assignment.objects.filter(
        course__in=enrolled_courses
    ).order_by('due_date').select_related('course')
    
    # Quickly retrieve all existing submissions for the user and these assignments
    submissions = Submission.objects.filter(student=user, assignment__in=assignments).in_bulk(field_name='assignment_id')
    now = timezone.now()
    
    assignment_data = []
    for assignment in assignments:
        submission = submissions.get(assignment.id)
        
        status = 'not_submitted'
        submission_id = None
        grade = None
        
        if submission:
            submission_id = submission.id
            grade = submission.grade
            if submission.grade is not None:
                status = 'graded'
            elif assignment.due_date < now:
                status = 'late' if submission.status == 'pending' else 'submitted'
            else:
                status = 'submitted'
        elif assignment.due_date < now:
            status = 'missed' # Missed deadline and never submitted
            
        assignment_data.append({
            'assignment': assignment,
            'submission_id': submission_id,
            'status': status,
            'grade': grade,
            'is_due': assignment.due_date < now
        })
        
    context = {
        'assignment_data': assignment_data,
        'page_title': 'My Assignments'
    }
    return render(request, 'student/assignment_list.html', context)


@user_passes_test(is_student)
def student_submit_assignment(request, assignment_id):
    """Student view to submit or update assignment content."""
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    user = request.user
    
    if not user.enrolled_courses.filter(pk=assignment.course.id).exists():
        messages.error(request, "You are not enrolled in the course for this assignment.")
        return redirect('student_assignment_list')

    # Get or create the submission
    submission, created = Submission.objects.get_or_create(student=user, assignment=assignment)

    if submission.grade is not None:
        messages.warning(request, "This submission has already been graded and cannot be modified.")
        return redirect('student_view_submission', submission_id=submission.id)

    if request.method == 'POST':
        form = StudentSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.submitted_at = timezone.now()
            
            # Set status based on due date
            if assignment.due_date < submission.submitted_at:
                submission.status = 'late'
            else:
                submission.status = 'pending'
                
            submission.save()
            messages.success(request, "Your submission has been saved successfully!")
            return redirect('student_assignment_list')
    else:
        form = StudentSubmissionForm(instance=submission)
        
    context = {
        'form': form,
        'assignment': assignment,
        'submission': submission,
        'page_title': f'Submit: {assignment.title}'
    }
    return render(request, 'student/submission_form.html', context)


@user_passes_test(is_student)
def student_view_submission(request, submission_id):
    """Student view to check the grade and feedback for a submission."""
    submission = get_object_or_404(
        Submission.objects.select_related('assignment__course', 'student', 'graded_by'), 
        pk=submission_id, 
        student=request.user
    )
    
    context = {
        'submission': submission,
        'page_title': f"Submission Detail: {submission.assignment.title}"
    }
    return render(request, 'student/submission_detail.html', context)


@user_passes_test(is_student)
def student_performance_view(request):
    """Student view to see overall grades and attendance summary."""
    user = request.user
    enrolled_courses = user.enrolled_courses.all()
    
    # 1. Grade Summary
    my_submissions = Submission.objects.filter(
        student=user,
        grade__isnull=False
    ).select_related('assignment__course').order_by('-assignment__due_date')
    
    avg_grade = my_submissions.aggregate(Avg('grade'))['grade__avg']
    
    # 2. Attendance Summary
    attendance_data = []
    
    for course in enrolled_courses:
        # Calculate total unique sessions for the course
        total_sessions = Attendance.objects.filter(course=course).values('date').distinct().count()
        
        # Student's attendance counts for that course
        present_count = Attendance.objects.filter(student=user, course=course, status='present').count()
        late_count = Attendance.objects.filter(student=user, course=course, status='late').count()
        absent_count = Attendance.objects.filter(student=user, course=course, status='absent').count()
        
        rate = (present_count / total_sessions * 100) if total_sessions > 0 else 0

        attendance_data.append({
            'course': course,
            'total_sessions': total_sessions,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'rate': f"{rate:.0f}%"
        })
        
    context = {
        'my_submissions': my_submissions,
        'avg_grade': f"{avg_grade:.2f}" if avg_grade is not None else 'N/A',
        'attendance_data': attendance_data,
        'page_title': 'My Performance Tracker'
    }
    return render(request, 'student/performance_view.html', context)
