from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Landing and Dashboard
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'), 
    
    # === ADMIN MANAGEMENT URLs ===
    # User Management
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/add/', views.admin_user_create, name='admin_user_create'), 
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    
    # Course/Unit Management
    path('admin/courses/', views.admin_course_list, name='admin_course_list'),
    path('admin/courses/add/', views.admin_course_create, name='admin_course_create'),
    path('admin/courses/<int:course_id>/edit/', views.admin_course_edit, name='admin_course_edit'), 
    
    # Assignment Assessment (Grading)
    path('admin/submissions/', views.admin_submission_list, name='admin_submission_list'), 
    path('admin/submissions/<int:submission_id>/grade/', views.admin_grade_submission, name='admin_grade_submission'),

    # Attendance
    path('admin/attendance/', views.admin_attendance, name='admin_attendance'),
    
    # === INSTRUCTOR MANAGEMENT URLs ===
    # Assignment CRUD
    path('instructor/assignments/', views.instructor_assignment_list, name='instructor_assignment_list'),
    path('instructor/assignments/create/', views.instructor_assignment_create, name='instructor_assignment_create'),
    path('instructor/assignments/<int:assignment_id>/edit/', views.instructor_assignment_edit, name='instructor_assignment_edit'),
    
    # Submission Grading
    path('instructor/submissions/', views.instructor_submission_list, name='instructor_submission_list'),
    path('instructor/submissions/<int:submission_id>/grade/', views.instructor_grade_submission, name='instructor_grade_submission'),

    # Attendance Management
    path('instructor/attendance/', views.instructor_attendance, name='instructor_attendance'),

    # Mailer Feature
    path('instructor/mailer/', views.instructor_mailer, name='instructor_mailer'),
    
    # Reporting Feature
    path('instructor/reports/', views.instructor_reports, name='instructor_reports'),

    # === STUDENT MANAGEMENT URLs ===
    # Assignments List
    path('student/assignments/', views.student_assignment_list, name='student_assignment_list'),
    # Submission Handling
    path('student/assignments/<int:assignment_id>/submit/', views.student_submit_assignment, name='student_submit_assignment'),
    path('student/submissions/<int:submission_id>/', views.student_view_submission, name='student_view_submission'),
    # Performance/Tracking
    path('student/performance/', views.student_performance_view, name='student_performance_view'),
]
