from django.db import models
from django.utils import timezone

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lecturer = models.CharField(max_length=100, blank=True, default="")  # <-- add this

    def __str__(self):
        return self.title


    class Meta:
        indexes = [
            models.Index(fields=["title"]),
        ]

class Assignment(models.Model):
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    # auto_now_add doesn't run during loaddata; give a real default:
    posted_at = models.DateTimeField(default=timezone.now, blank=True)


    def __str__(self):
        return f"{self.title} • {self.course.title}"

    class Meta:
        indexes = [
            models.Index(fields=["course", "due_date"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["course", "title"], name="uq_assignment_course_title")
        ]
