from django.db import models

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    semester = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.title} ({self.semester})"

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
        ]

class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} • {self.course.title}"

    class Meta:
        indexes = [
            models.Index(fields=["course", "due_date"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["course", "title"], name="uq_assignment_course_title")
        ]
