from django.contrib import admin
from .models import Attendance, Lesson, StudyGroup


admin.site.register(StudyGroup)
admin.site.register(Lesson)
admin.site.register(Attendance)
