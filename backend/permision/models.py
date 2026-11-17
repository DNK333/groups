from django.db import models
from django.contrib.auth.models import AbstractUser, User

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    birth_data = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username

class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='articles'
    )

    def __str__(self):
        return self.title



class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='user_comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.article}"




class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name



