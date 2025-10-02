from django.db import models
from users.models import Lecturer

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    semester = models.CharField(max_length=20, blank=True)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.PROTECT, null=True, blank=True, related_name="courses")

    def __str__(self):
        return f"{self.title} ({self.semester})"

    class Meta:
        indexes = [models.Index(fields=["title"])]
