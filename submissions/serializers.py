from rest_framework import serializers
from .models import Submission
from users.serializers import UserSerializer
from assignments.serializers import AssignmentSerializer

class SubmissionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    assignment = AssignmentSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'file', 'submitted_at', 'grade', 'feedback', 'student', 'assignment']

class SubmissionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'file', 'assignment']

    def create(self, validated_data):
        # automatically assign student based on request user
        request = self.context.get('request')
        validated_data['student'] = request.user
        return super().create(validated_data)