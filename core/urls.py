from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('courses/', views.course_list, name='course_list'),
    path('course/create/', views.create_course, name='create_course'),
    path('course/<int:course_id>/question/create/', views.create_question, name='create_question'),
    path('course/<int:course_id>/questions/', views.question_list, name='question_list'),
    path('exam/take/<int:course_id>/', views.take_exam, name='take_exam'),
    path('exam/results/<int:course_id>/', views.results, name='results'),
    path('teachers/', views.teacher_management, name='teacher_management'),
    path('students/', views.student_management, name='student_management'),
    path('course/<int:course_id>/progress/', views.student_progress, name='student_progress'),  # Новий URL
]