from django.db import models
from django.conf import settings


class StudyGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="study_groups",
        blank=True,
    )

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=150)
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="lessons",
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teaching_lessons",
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    def __str__(self):
        return f"{self.title} ({self.starts_at:%Y-%m-%d %H:%M})"


class Attendance(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    is_present = models.BooleanField()
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="marked_attendance_records",
    )
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("lesson", "student"),
                name="unique_attendance_per_lesson_student",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.lesson}"
