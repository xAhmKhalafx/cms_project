from django.db import models
from assignments.models import Assignment
from users.models import Student

def submission_upload_path(instance, filename):
    return f"submissions/{instance.assignment_id}/{instance.student_id}/{filename}"

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to=submission_upload_path, blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["assignment", "student"], name="uq_submission_assignment_student")]
        indexes = [models.Index(fields=["assignment", "student"])]

    def __str__(self):
        return f"S{self.submission_id} • A{self.assignment_id} • Stu{self.student_id}"
