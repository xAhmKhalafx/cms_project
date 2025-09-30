from django.db import models
from assignments.models import Assignment
from users.models import Student

def submission_upload_path(instance, filename):
    # media/submissions/<assignment_id>/<student_id>/<filename>
    return f"submissions/{instance.assignment_id}/{instance.student_id}/{filename}"

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to=submission_upload_path, blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission #{self.submission_id} — A{self.assignment_id} • S{self.student_id}"

    class Meta:
        constraints = [
            # one submission record per student per assignment
            models.UniqueConstraint(fields=["assignment", "student"], name="uq_submission_assignment_student")
        ]
        indexes = [
            models.Index(fields=["assignment", "student"]),
        ]
