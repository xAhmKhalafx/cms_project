from django.db import models
from courses.models import Course

class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["course", "due_date"])]
        constraints = [models.UniqueConstraint(fields=["course", "title"], name="uq_assignment_course_title")]

    def __str__(self):
        return f"{self.title} • {self.course.title}"
