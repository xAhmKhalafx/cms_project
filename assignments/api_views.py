from rest_framework import viewsets, permissions
from courses.permissions import IsLecturer
from .models import Assignment
from .serializers import AssignmentSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer

    def get_queryset(self):
        course_id = self.request.query_params.get("course")
        qs = Assignment.objects.all().order_by("-due_date")
        return qs.filter(course_id=course_id) if course_id else qs

    def get_permissions(self):
        # Only lecturers can create/update/delete; anyone can GET
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated(), IsLecturer()]
        return [permissions.AllowAny()]
