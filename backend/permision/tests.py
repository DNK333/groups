from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Article, Comment, Product
from .models import CustomUser


class RoleAndContentApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher_group, _ = Group.objects.get_or_create(name="Teacher")
        cls.student_group, _ = Group.objects.get_or_create(name="Student")
        cls.admin_group, _ = Group.objects.get_or_create(name="Admin")

        cls.teacher = CustomUser.objects.create_user(
            username="teacher",
            password="password",
        )
        cls.teacher.groups.add(cls.teacher_group)
        cls.other_teacher = CustomUser.objects.create_user(
            username="other_teacher",
            password="password",
        )
        cls.other_teacher.groups.add(cls.teacher_group)
        cls.student = CustomUser.objects.create_user(
            username="student",
            password="password",
        )
        cls.student.groups.add(cls.student_group)
        cls.admin = CustomUser.objects.create_user(
            username="admin",
            password="password",
        )
        cls.admin.groups.add(cls.admin_group)

        cls.own_article = Article.objects.create(
            title="Own article",
            content="Original",
            author=cls.teacher,
        )
        cls.other_article = Article.objects.create(
            title="Other article",
            content="Original",
            author=cls.other_teacher,
        )
        cls.product = Product.objects.create(name="Book", price="12.50")

    def setUp(self):
        self.client = APIClient()

    def test_student_permission_is_group_based(self):
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get("/api/student/").status_code, 200)

        self.client.force_authenticate(self.teacher)
        self.assertEqual(self.client.get("/api/student/").status_code, 403)

    def test_current_user_endpoint_returns_any_authenticated_user(self):
        self.client.force_authenticate(self.student)
        response = self.client.get("/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], self.student.username)
        self.assertIn("Student", response.data["groups"])

    def test_teacher_can_read_any_article_but_only_edit_own(self):
        self.client.force_authenticate(self.teacher)
        detail_url = f"/api/articles/{self.other_article.pk}/"
        self.assertEqual(self.client.get(detail_url).status_code, 200)
        self.assertEqual(
            self.client.patch(detail_url, {"title": "Changed"}, format="json").status_code,
            403,
        )
        self.assertEqual(
            self.client.patch(
                f"/api/articles/{self.own_article.pk}/",
                {"title": "Changed"},
                format="json",
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(f"/api/articles/{self.own_article.pk}/").status_code,
            403,
        )

    def test_admin_can_edit_and_delete_any_article(self):
        self.client.force_authenticate(self.admin)
        detail_url = f"/api/articles/{self.other_article.pk}/"
        self.assertEqual(
            self.client.patch(detail_url, {"title": "Admin edit"}, format="json").status_code,
            200,
        )
        self.assertEqual(self.client.delete(detail_url).status_code, 204)

    def test_comments_list_and_create_endpoint(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            "/api/comments/",
            {"article": self.own_article.pk, "text": "Useful article"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["author"], self.student.pk)
        self.assertEqual(self.client.get("/api/comments/").status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)

    def test_product_detail_can_be_retrieved_updated_and_deleted(self):
        self.client.force_authenticate(self.student)
        detail_url = f"/api/products/{self.product.pk}/"
        self.assertEqual(self.client.get(detail_url).status_code, 200)
        response = self.client.patch(
            detail_url,
            {"price": "15.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["price"], "15.00")
        self.assertEqual(self.client.delete(detail_url).status_code, 204)
