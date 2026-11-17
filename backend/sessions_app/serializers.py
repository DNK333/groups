from django.contrib.auth import get_user_model
from rest_framework import serializers

from permision.permissions import is_admin
from .models import Attendance, Lesson, StudyGroup


class StudyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyGroup
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ("teacher",)

    def validate(self, attrs):
        starts_at = attrs.get(
            "starts_at",
            self.instance.starts_at if self.instance is not None else None,
        )
        ends_at = attrs.get(
            "ends_at",
            self.instance.ends_at if self.instance is not None else None,
        )
        if starts_at is not None and ends_at is not None and ends_at <= starts_at:
            raise serializers.ValidationError(
                {"ends_at": "Lesson must end after it starts."}
            )
        return attrs


class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
    )

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = ("marked_by", "marked_at")

    def validate(self, attrs):
        lesson = attrs.get(
            "lesson",
            self.instance.lesson if self.instance is not None else None,
        )
        student = attrs.get(
            "student",
            self.instance.student if self.instance is not None else None,
        )
        if (
            lesson is not None
            and student is not None
            and not lesson.group.students.filter(pk=student.pk).exists()
        ):
            raise serializers.ValidationError(
                {"student": "Student must belong to the lesson's study group."}
            )
        request = self.context.get("request")
        if (
            lesson is not None
            and request is not None
            and not is_admin(request.user)
            and lesson.teacher_id != request.user.id
        ):
            raise serializers.ValidationError(
                {"lesson": "You can only mark attendance for your own lessons."}
            )
        return attrs
