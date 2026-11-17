from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

# Получаем вашу кастомную модель пользователя (permision.CustomUser)
User = get_user_model()


class RegisterForm(UserCreationForm):

  class Meta(UserCreationForm.Meta):
    model = User
    fields = ['username']  # password1 и password2 добавляются автоматически

  def save(self, commit=True):
    user = super().save(commit=commit)

    if commit:
      group, created = Group.objects.get_or_create(name='Student')
      user.groups.add(group)

    return user


class RegisterFormJKArman(UserCreationForm):

  class Meta(UserCreationForm.Meta):
    model = User
    fields = ['username']

  def save(self, commit=True):
    user = super().save(commit=commit)

    if commit:
      group, created = Group.objects.get_or_create(name='JSArman')
      user.groups.add(group)

    return user


class RegisterFormChoice(UserCreationForm):
  role = forms.ChoiceField(
      choices=[('Student', 'Student'), ('Teacher', 'Teacher')]
  )

  class Meta(UserCreationForm.Meta):
    model = User
    fields = ['username']

  def save(self, commit=True):
    user = super().save(commit=commit)

    if commit:
      role = self.cleaned_data['role']
      group, created = Group.objects.get_or_create(name=role)
      user.groups.add(group)

    return user
