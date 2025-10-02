from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Submission
from .serializers import SubmissionSerializer
from users.models import Student

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "student_profile")

class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "lecturer_profile")

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all().order_by("-submitted_at")
    serializer_class = SubmissionSerializer

    def get_permissions(self):
        if self.action in ["create", "my_submissions"]:
            return [permissions.IsAuthenticated(), IsStudent()]
        if self.action in ["grade"]:
            return [permissions.IsAuthenticated(), IsLecturer()]
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]  # tighten if needed
        return [permissions.AllowAny()]

    @action(detail=False, methods=["GET"])
    def my_submissions(self, request):
        student = request.user.student_profile
        qs = Submission.objects.filter(student=student).order_by("-submitted_at")
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=["POST"])
    def grade(self, request, pk=None):
        sub = self.get_object()
        grade = request.data.get("grade")
        feedback = request.data.get("feedback", "")
        sub.grade = float(grade)
        sub.feedback = feedback
        sub.save()
        return Response(self.get_serializer(sub).data, status=status.HTTP_200_OK)
