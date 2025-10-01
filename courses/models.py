from django.db import models
from users.models import User # IMPORTANT: Import the custom User model

# Course Model (courses_course)
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # CRITICAL CHANGE: Must be a ForeignKey to User for role-based access
    lecturer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role': 'instructor'}, # Only allow instructors
        related_name='taught_courses',
        verbose_name='Lecturer'
    )
    
    # NEW FIELD: Many-to-Many field for student enrollment
    students = models.ManyToManyField(
        User, 
        related_name='enrolled_in_courses', # <-- CHANGED related_name
        limit_choices_to={'role': 'student'},
        blank=True
    )

    def __str__(self):
        return self.title

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Keeping this as DateField as requested, but generally DateTimeField is preferred for deadlines
    due_date = models.DateField() 

    def __str__(self):
        return f"{self.title} ({self.course.title})"

    class Meta:
        ordering = ['due_date']

# NEW FEATURE MODEL: Attendance (Editable by Admin/Lecturer)
class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_attendance')
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'},
        related_name='attendance_records'
    )
    # Date of the class session
    session_date = models.DateField()
    
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('E', 'Excused'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    marked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_attendance'
    )


    def __str__(self):
        return f"{self.student.last_name} ({self.status}) for {self.course.title} on {self.session_date}"

    class Meta:
        # Ensures only one attendance record per student per course per session date
        unique_together = ('course', 'student', 'session_date')
        ordering = ['session_date']
