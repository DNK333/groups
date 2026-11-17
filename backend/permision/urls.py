from django.urls import path, reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from sessions_app.views import home, forget
from .views import (
    register,
    register_JKArman,
    register_choice,
    response_perm,
    CustomLoginView,
    profile,
    CurrentUserView,
    TeacherView,
    ArticleListView,
    ArticleListCreateView,
    CommentListView,
    CommentListCreateView,
    ArticleDetailView
)

urlpatterns = [
    path(
        'change_password/', PasswordChangeView.as_view(
            template_name='permision/change.html',
            success_url=reverse_lazy('profile')
        ), 
        name='change_password'
    ),
    path("api/articles/<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
    path("api/comment/create/", CommentListCreateView.as_view(), name="comments_list"),
    path("api/comments/", CommentListView.as_view(), name="comment_create"),
    path("api/article/create/", ArticleListCreateView.as_view(), name="article_list"),
    path("api/articles/", ArticleListView.as_view(), name="article_create"),
    path("api/teacher/", TeacherView.as_view(), name="teacher"),
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('home/', home, name='home'),
    path('forget/', forget, name='forget'),
    path('profile/', profile, name='profile'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('response_perm/', response_perm, name='response_perm'),
    path('register_choice/', register_choice, name='register_choice'),
    path('register_JKArman/', register_JKArman, name='register_JKArman'),
]
