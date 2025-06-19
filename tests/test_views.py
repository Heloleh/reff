import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Course, Teacher, Question, ExamAttempt

@pytest.mark.django_db
def test_signup_get(client):
    response = client.get(reverse('signup'))
    assert response.status_code == 200
    assert b'Sign Up' in response.content or b'form' in response.content

@pytest.mark.django_db
def test_dashboard_student(client):
    student = User.objects.create_user(username='student1', password='pass')
    client.login(username='student1', password='pass')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_dashboard_teacher_unapproved(client):
    user = User.objects.create_user(username='teacher1', password='pass')
    Teacher.objects.create(user=user, is_approved=False)
    client.login(username='teacher1', password='pass')
    response = client.get(reverse('dashboard'))
    assert b'awaiting' in response.content.lower()

@pytest.mark.django_db
def test_course_list_view(client):
    user = User.objects.create_user(username='u', password='p')
    client.login(username='u', password='p')
    response = client.get(reverse('course_list'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_create_course_permission_denied(client):
    user = User.objects.create_user(username='no_rights', password='p')
    client.login(username='no_rights', password='p')
    response = client.get(reverse('create_course'))
    assert response.status_code == 302  # redirect

@pytest.mark.django_db
def test_question_list(client):
    user = User.objects.create_user(username='q1', password='p')
    course = Course.objects.create(name='Course1', description='desc', created_by=user)
    client.login(username='q1', password='p')
    response = client.get(reverse('question_list', args=[course.id]))
    assert response.status_code == 200

@pytest.mark.django_db
def test_take_exam_post(client):
    user = User.objects.create_user(username='exam2', password='p')
    course = Course.objects.create(name='Course3', description='desc', created_by=user)
    q = Question.objects.create(course=course, text='Q?', option1='A', option2='B', option3='C', option4='D', correct_option=2, marks=1)
    client.login(username='exam2', password='p')
    data = {f'question_{q.id}': '2'}
    response = client.post(reverse('take_exam', args=[course.id]), data)
    assert response.status_code == 302  # Redirect after submit
    assert ExamAttempt.objects.filter(student=user, course=course).exists()

@pytest.mark.django_db
def test_results_view(client):
    user = User.objects.create_user(username='ruser', password='p')
    course = Course.objects.create(name='Course4', description='desc', created_by=user)
    ExamAttempt.objects.create(student=user, course=course, score=5)
    client.login(username='ruser', password='p')
    response = client.get(reverse('results', args=[course.id]))
    assert response.status_code == 200

@pytest.mark.django_db
def test_teacher_management_access(client):
    admin = User.objects.create_superuser(username='admin', password='admin')
    client.login(username='admin', password='admin')
    response = client.get(reverse('teacher_management'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_student_management_access(client):
    admin = User.objects.create_superuser(username='admin2', password='admin2')
    client.login(username='admin2', password='admin2')
    response = client.get(reverse('student_management'))
    assert response.status_code == 200