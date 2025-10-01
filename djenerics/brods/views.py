from rest_framework import viewsets
from brods.models import Course, Lesson
from brods.serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import AllowAny

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [AllowAny]