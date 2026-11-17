from django.urls import path
from .views import (
    AttendanceDetailView,
    AttendanceListCreateView,
    LessonDetailView,
    LessonListCreateView,
    StudyGroupDetailView,
    StudyGroupListCreateView,
)

urlpatterns = [
    path("study-groups/", StudyGroupListCreateView.as_view(), name="study_group_list"),
    path(
        "study-groups/<int:pk>/",
        StudyGroupDetailView.as_view(),
        name="study_group_detail",
    ),
    path("lessons/", LessonListCreateView.as_view(), name="lesson_list"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson_detail"),
    path("attendance/", AttendanceListCreateView.as_view(), name="attendance_list"),
    path(
        "attendance/<int:pk>/",
        AttendanceDetailView.as_view(),
        name="attendance_detail",
    ),
]
