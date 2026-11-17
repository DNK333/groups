from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from permision.models import CustomUser
from .models import Attendance, Lesson, StudyGroup


class StudyScheduleAndAttendanceApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        teacher_role, _ = Group.objects.get_or_create(name="Teacher")
        student_role, _ = Group.objects.get_or_create(name="Student")

        cls.teacher = CustomUser.objects.create_user(
            username="schedule_teacher",
            password="password",
        )
        cls.teacher.groups.add(teacher_role)
        cls.other_teacher = CustomUser.objects.create_user(
            username="other_schedule_teacher",
            password="password",
        )
        cls.other_teacher.groups.add(teacher_role)
        cls.student = CustomUser.objects.create_user(
            username="schedule_student",
            password="password",
        )
        cls.student.groups.add(student_role)
        cls.other_student = CustomUser.objects.create_user(
            username="other_schedule_student",
            password="password",
        )
        cls.other_student.groups.add(student_role)

        cls.group = StudyGroup.objects.create(name="Group A")
        cls.group.students.add(cls.student)
        cls.other_group = StudyGroup.objects.create(name="Group B")
        cls.other_group.students.add(cls.other_student)
        cls.lesson = Lesson.objects.create(
            title="Algebra",
            group=cls.group,
            teacher=cls.teacher,
            starts_at="2026-11-18T09:00:00Z",
            ends_at="2026-11-18T10:00:00Z",
        )
        cls.other_lesson = Lesson.objects.create(
            title="Physics",
            group=cls.other_group,
            teacher=cls.other_teacher,
            starts_at="2026-11-18T10:00:00Z",
            ends_at="2026-11-18T11:00:00Z",
        )
        cls.attendance = Attendance.objects.create(
            lesson=cls.lesson,
            student=cls.student,
            is_present=True,
            marked_by=cls.teacher,
        )

    def setUp(self):
        self.client = APIClient()

    def test_student_sees_only_own_group_schedule_and_search_works(self):
        self.client.force_authenticate(self.student)
        response = self.client.get("/api/lessons/?search=algebra")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([lesson["id"] for lesson in response.data], [self.lesson.pk])
        self.assertEqual(
            self.client.get(f"/api/lessons/{self.other_lesson.pk}/").status_code,
            404,
        )

    def test_teacher_can_create_lessons_but_not_edit_another_teachers_lesson(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            "/api/lessons/",
            {
                "title": "Geometry",
                "group": self.group.pk,
                "starts_at": "2026-11-19T09:00:00Z",
                "ends_at": "2026-11-19T10:00:00Z",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["teacher"], self.teacher.pk)
        self.assertEqual(
            self.client.patch(
                f"/api/lessons/{self.other_lesson.pk}/",
                {"title": "Changed"},
                format="json",
            ).status_code,
            404,
        )

    def test_teacher_marks_attendance_only_for_their_own_lesson(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            "/api/attendance/",
            {
                "lesson": self.lesson.pk,
                "student": self.student.pk,
                "is_present": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)

        response = self.client.post(
            "/api/attendance/",
            {
                "lesson": self.other_lesson.pk,
                "student": self.other_student.pk,
                "is_present": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("lesson", response.data)

        self.assertEqual(
            self.client.patch(
                f"/api/attendance/{self.attendance.pk}/",
                {"is_present": False},
                format="json",
            ).status_code,
            200,
        )

        other_attendance = Attendance.objects.create(
            lesson=self.other_lesson,
            student=self.other_student,
            is_present=True,
            marked_by=self.other_teacher,
        )
        self.assertEqual(
            self.client.patch(
                f"/api/attendance/{other_attendance.pk}/",
                {"is_present": False},
                format="json",
            ).status_code,
            404,
        )

    def test_students_can_only_read_their_own_attendance(self):
        self.client.force_authenticate(self.student)
        response = self.client.get("/api/attendance/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([record["id"] for record in response.data], [self.attendance.pk])
        self.assertEqual(
            self.client.patch(
                f"/api/attendance/{self.attendance.pk}/",
                {"is_present": False},
                format="json",
            ).status_code,
            403,
        )

    def test_admin_can_manage_study_groups(self):
        admin_role, _ = Group.objects.get_or_create(name="Admin")
        admin = CustomUser.objects.create_user(username="schedule_admin")
        admin.groups.add(admin_role)
        self.client.force_authenticate(admin)
        response = self.client.post(
            "/api/study-groups/",
            {"name": "Group C"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(StudyGroup.objects.filter(name="Group C").exists())
