from django.db import models

def submission_upload_path(instance, filename):
    return f"submissions/{instance.assignment_id}/{instance.student_id}/{filename}"

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey('assignments.Assignment', on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to=submission_upload_path, blank=True, null=True)
    grade = models.FloatField(blank=True, null=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
