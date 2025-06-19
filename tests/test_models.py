import pytest
from django.contrib.auth.models import User
from core.models import Teacher, Course, Question, ExamAttempt

@pytest.mark.django_db
def test_teacher_str():
    user = User.objects.create_user(username='teacher1', password='pass')
    teacher = Teacher.objects.create(user=user)
    assert str(teacher) == 'teacher1'

@pytest.mark.django_db
def test_teacher_default_approval():
    user = User.objects.create_user(username='t2', password='p')
    teacher = Teacher.objects.create(user=user)
    assert not teacher.is_approved

@pytest.mark.django_db
def test_course_str():
    user = User.objects.create_user(username='u1', password='p')
    course = Course.objects.create(name='Math', description='desc', created_by=user)
    assert str(course) == 'Math'

@pytest.mark.django_db
def test_question_str():
    user = User.objects.create_user(username='u2', password='p')
    course = Course.objects.create(name='Biology', description='desc', created_by=user)
    question = Question.objects.create(course=course, text='What is DNA?', option1='A', option2='B',
                                       option3='C', option4='D', correct_option=1, marks=2)
    assert str(question) == 'What is DNA?'

@pytest.mark.django_db
def test_exam_attempt_str():
    user = User.objects.create_user(username='s1', password='p')
    teacher = User.objects.create_user(username='t1', password='p')
    course = Course.objects.create(name='History', description='WW2', created_by=teacher)
    attempt = ExamAttempt.objects.create(student=user, course=course, score=10)
    assert str(attempt) == f"{user.username} - {course.name} - {attempt.score}"

@pytest.mark.django_db
def test_question_correct_option_choices():
    correct_choices = [1, 2, 3, 4]
    for choice in correct_choices:
        assert (choice, choice) in Question._meta.get_field('correct_option').choices

@pytest.mark.django_db
def test_exam_attempt_progress_default():
    user = User.objects.create_user(username='s2', password='p')
    course = Course.objects.create(name='Chem', description='desc', created_by=user)
    attempt = ExamAttempt.objects.create(student=user, course=course, score=0)
    assert attempt.progress_percentage == 0.0
