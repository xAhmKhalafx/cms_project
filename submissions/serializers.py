# submissions/serializers.py
from rest_framework import serializers
from .models import Submission

class SubmissionSerializer(serializers.ModelSerializer):
    """
    Basic serializer for create/update.
    Expects `assignment` and `student` as PKs; `file` is optional if your model allows it.
    """
    class Meta:
        model = Submission
        fields = [
            "submission_id",
            "assignment",     # FK (assignment_id as integer)
            "student",        # FK (student_id as integer)
            "file",           # FileField; DRF will return URL if MEDIA is configured
            "grade",
            "feedback",
            "submitted_at",
        ]
        read_only_fields = ["submission_id", "submitted_at"]


class SubmissionReadSerializer(serializers.ModelSerializer):
    """
    Read-friendly serializer: adds useful labels for UI/JSON.
    """
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    course_id = serializers.IntegerField(source="assignment.course_id", read_only=True)
    student_username = serializers.CharField(source="student.user.username", read_only=True)
    file_url = serializers.FileField(source="file", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "submission_id",
            "assignment",
            "assignment_title",
            "course_id",
            "student",
            "student_username",
            "file_url",
            "grade",
            "feedback",
            "submitted_at",
        ]
        read_only_fields = fields
