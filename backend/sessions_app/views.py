from django.shortcuts import redirect, render
from django.db.models import QuerySet
from rest_framework import filters
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated

from permision.permissions import (
    CanManageAttendance,
    CanManageLessons,
    IsAdminOrReadOnly,
    is_admin,
    is_student,
    is_teacher,
)
from .models import Attendance, Lesson, StudyGroup
from .serializers import AttendanceSerializer, LessonSerializer, StudyGroupSerializer


def home(request):
    if request.method == "POST":
        name = request.POST.get("name")
        request.session["username"] = name
        return redirect("home")

    username = request.session.get("username")
    return render(request, "sessions_app/home.html", {"username": username})


def forget(request):
    request.session.pop("username", None)
    return redirect("home")


def visible_study_groups(user) -> QuerySet[StudyGroup]:
    groups = StudyGroup.objects.prefetch_related("students")
    if is_admin(user) or is_teacher(user):
        return groups
    if is_student(user):
        return groups.filter(students=user)
    return groups.none()


class StudyGroupListCreateView(ListCreateAPIView):
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return visible_study_groups(self.request.user)


class StudyGroupDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return visible_study_groups(self.request.user)


class LessonListCreateView(ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [CanManageLessons]
    filter_backends = [filters.SearchFilter]
    search_fields = ("title",)

    def get_queryset(self):
        lessons = Lesson.objects.select_related("group", "teacher")
        user = self.request.user
        if is_admin(user):
            pass
        elif is_teacher(user):
            lessons = lessons.filter(teacher=user)
        elif is_student(user):
            lessons = lessons.filter(group__students=user)
        else:
            return lessons.none()

        group_id = self.request.query_params.get("group")
        if group_id:
            lessons = lessons.filter(group_id=group_id)
        teacher_id = self.request.query_params.get("teacher")
        if teacher_id and is_admin(user):
            lessons = lessons.filter(teacher_id=teacher_id)
        return lessons

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class LessonDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [CanManageLessons]

    def get_queryset(self):
        return LessonListCreateView.get_queryset(self)


class AttendanceListCreateView(ListCreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [CanManageAttendance]

    def get_queryset(self):
        records = Attendance.objects.select_related(
            "lesson__group",
            "lesson__teacher",
            "student",
            "marked_by",
        )
        user = self.request.user
        if is_admin(user):
            return records
        if is_teacher(user):
            return records.filter(lesson__teacher=user)
        if is_student(user):
            return records.filter(student=user)
        return records.none()

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)


class AttendanceDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [CanManageAttendance]

    def get_queryset(self):
        return AttendanceListCreateView.get_queryset(self)

    def perform_update(self, serializer):
        serializer.save(marked_by=self.request.user)
