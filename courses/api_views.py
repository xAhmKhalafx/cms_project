from rest_framework import viewsets, permissions
from .models import Course
from .serializers import CourseSerializer
from .permissions import IsLecturer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("title")
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated(), IsLecturer()]
        return [permissions.AllowAny()]
