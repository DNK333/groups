from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from .forms import RegisterForm, RegisterFormJKArman, RegisterFormChoice
from django.http import JsonResponse, HttpResponse
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import (
    ArticlePermissions,
    IsArticleOwnerOrAdmin,
    IsStudent,
    IsTeacher,
)
from .models import Article, Comment, Product
from .serializers import ArticleSerializer, CommentSerializer, ProductSerializer

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            return redirect('register')
        
    else:
        form = RegisterForm()
        
    return render(request, 'permision/register.html', {
        "form": form
    })


def register_choice(request):
    if request.method == "POST":
        form = RegisterFormChoice(request.POST)
        
        if form.is_valid():
            user = form.save()
            return redirect('register_choice')
        
    else:
        form = RegisterFormChoice()
        
    return render(request, 'permision/register.html', {
        "form": form
    })
    
def register_JKArman(request):
    if request.method == "POST":
        form = RegisterFormJKArman(request.POST)
        
        if form.is_valid():
            user = form.save()
            return redirect('register_JKArman')
        
    else:
        form = RegisterFormJKArman()
        
    return render(request, 'permision/register.html', {
        "form": form
    })

def add_user_to_student_group(user):
    group, _ = Group.objects.get_or_create(name="Student")
    user.groups.add(group)
    
def add_user_to_teacher_group(user):
    group, _ = Group.objects.get_or_create(name="Teacher")
    user.groups.add(group)
    
    
def check_article_ermission(user):
    return user.has_perm('permision.view_article')



def response_perm(request):
    if request.user.has_perm('permision.add_article'):
        return JsonResponse({"Message1": "True"})
    
    return JsonResponse({"Message2": "False"}, status=403)

class CustomLoginView(LoginView):
    template_name = 'permision/login.html'
  
def profile(request):
    user = request.user
    
    if user.is_authenticated:
        return HttpResponse(
            f"Привет, {user.username}! ты авторизован(-а)"
        )
        
    return HttpResponse("Ты не авторизован")
  
  
class CurrentUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "is_authenticated": user.is_authenticated,
            "is_staff": user.is_staff,
            "groups": list(user.groups.values_list("name", flat=True)),
        })
           
           
class TeacherView(GenericAPIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        return Response({
            'message': 'Добро пожаловать, преподаватель',
            'username': request.user.username
        }) 


class StudentView(GenericAPIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return Response({
            'message': 'Добро пожаловать, студент',
            'username': request.user.username
        })
    
            
def test_serializer():       
    article = Article.objects.all()
    
    serializer = ArticleSerializer(article)
    
    return serializer.data

class ArticleListView(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermissions]
    
class ArticleListCreateView(ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [ArticlePermissions]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  

class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_permissions(self):
        permissions = [ArticlePermissions()]
        if self.request.method not in ("GET", "HEAD", "OPTIONS"):
            permissions.append(IsArticleOwnerOrAdmin())
        return permissions

class CommentListView(ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
class CommentListCreateView(ListCreateAPIView):
    queryset = Comment.objects.select_related("article", "author").all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
        

# request.user.is_authenticated
# request.user.is_staff
# request.user.is_superuser
# request.user.groups.all()
