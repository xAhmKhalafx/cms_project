from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Assignment
from .serializers import CourseSerializer, AssignmentSerializer
from .permissions import IsLecturer

@api_view(['GET'])
def list_courses(request):
    """
    GET /api/courses/
    Returns all courses.
    """
    qs = Course.objects.all().order_by('title')
    data = CourseSerializer(qs, many=True).data
    return Response(data)

@api_view(['GET'])
def list_course_assignments(request, course_id):
    """
    GET /api/courses/<course_id>/assignments/
    Returns assignments for a specific course.
    """
    qs = Assignment.objects.filter(course_id=course_id).order_by('-due_date')
    data = AssignmentSerializer(qs, many=True).data
    return Response(data)

@api_view(['POST'])
@permission_classes([IsLecturer])  # change to [] if you haven't set roles yet
def create_assignment(request, course_id):
    """
    POST /api/courses/<course_id>/assignments/create/
    Creates a new assignment under a specific course.
    Expected JSON: { "title": "...", "description": "...", "due_date": "YYYY-MM-DD" }
    """
    payload = request.data.copy()
    payload['course'] = course_id  # attach course from URL
    ser = AssignmentSerializer(data=payload)
    if ser.is_valid():
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
