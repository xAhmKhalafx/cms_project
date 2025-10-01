# submissions/models.py

from django.db import models
# Import models from other apps
from courses.models import Assignment  # Assuming 'Assignment' is in your 'courses' app
from users.models import User         # Assuming your custom User model is here

class Submission(models.Model):
    # Relate the submission to a specific assignment
    assignment = models.ForeignKey(
        Assignment, 
        on_delete=models.CASCADE, 
        related_name='submissions'
    )
    
    # Relate the submission to the student who submitted it
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'}, # Only students can submit
        related_name='submissions'
    )
    
    # File field for the actual submitted file (e.g., PDF, DOCX, ZIP)
    file = models.FileField(upload_to='submissions/') 
    
    # Date/Time of submission
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for grading
    grade = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Optional text feedback
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f"Submission for {self.assignment.title} by {self.student.last_name}"

    class Meta:
        # Ensures a student can only submit once per assignment
        unique_together = ('assignment', 'student')
        ordering = ['submitted_at']

# Now that Submission is defined, the import in submissions/forms.py will work.