from django.contrib import admin
from .models import Teacher, Course, Question, ExamAttempt

admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Question)
admin.site.register(ExamAttempt)