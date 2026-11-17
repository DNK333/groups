from rest_framework.permissions import BasePermission


def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="Admin").exists()
    )


def is_teacher(user):
    return user.is_authenticated and user.groups.filter(name="Teacher").exists()


def is_student(user):
    return user.is_authenticated and user.groups.filter(name="Student").exists()


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return is_teacher(request.user)


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return is_student(request.user)


class ArticlePermissions(BasePermission):
    def has_permission(self, request, view):
        return is_teacher(request.user) or is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return is_teacher(request.user)

        if request.method in ("PUT", "PATCH"):
            return is_teacher(request.user) and obj.author_id == request.user.id

        return False


class IsArticleOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author_id == request.user.id or is_admin(request.user)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.method in ("GET", "HEAD", "OPTIONS") or is_admin(request.user)
        )


class CanManageLessons(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            is_admin(request.user)
            or is_teacher(request.user)
            or (
                request.method in ("GET", "HEAD", "OPTIONS")
                and is_student(request.user)
            )
        )

    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True
        if is_teacher(request.user):
            return obj.teacher_id == request.user.id
        return (
            request.method in ("GET", "HEAD", "OPTIONS")
            and is_student(request.user)
            and obj.group.students.filter(pk=request.user.pk).exists()
        )


class CanManageAttendance(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            is_admin(request.user)
            or is_teacher(request.user)
            or (
                request.method in ("GET", "HEAD", "OPTIONS")
                and is_student(request.user)
            )
        )

    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True
        if is_teacher(request.user):
            return obj.lesson.teacher_id == request.user.id
        return (
            request.method in ("GET", "HEAD", "OPTIONS")
            and is_student(request.user)
            and obj.student_id == request.user.id
        )


class IsArticleOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
