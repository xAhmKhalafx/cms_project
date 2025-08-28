from rest_framework import serializers
from .models import Course
from users.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
    instructors = UserSerializer(many=True, read_only=True)
    students = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'code', 'description', 'start_date', 'end_date', 'instructors', 'students']

class CourseWriteSerializer(serializers.ModelSerializer):
    instructor_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='instructor'), many=True, write_only=True)
    student_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='student'), many=True, write_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'code', 'description', 'start_date', 'end_date', 'instructor_ids', 'student_ids']

    def create(self, validated_data):
        instructors = validated_data.pop('instructor_ids', [])
        students = validated_data.pop('student_ids', [])
        course = Course.objects.create(**validated_data)
        course.instructors.set(instructors)
        course.students.set(students)
        return course