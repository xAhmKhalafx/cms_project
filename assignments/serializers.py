# assignments/serializers.py
from rest_framework import serializers
from .models import Assignment

class AssignmentSerializer(serializers.ModelSerializer):
    """
    Basic serializer: accepts/returns PK for `course`.
    Good for POST/PUT/PATCH.
    """
    class Meta:
        model = Assignment
        fields = [
            "assignment_id",
            "course",          # FK (course_id as integer)
            "title",
            "description",
            "due_date",
            "posted_at",
        ]
        read_only_fields = ["assignment_id", "posted_at"]


class AssignmentReadSerializer(serializers.ModelSerializer):
    """
    Read-friendly serializer: adds course title and a submissions count.
    Use for GET list/detail.
    """
    course_title = serializers.CharField(source="course.title", read_only=True)
    submissions_count = serializers.IntegerField(source="submissions.count", read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "assignment_id",
            "title",
            "description",
            "due_date",
            "posted_at",
            "course",          # still returns PK
            "course_title",    # extra, read-only
            "submissions_count",
        ]
        read_only_fields = fields
