import pytest
from core.forms import SignUpForm, CourseForm, QuestionForm

@pytest.mark.django_db
def test_valid_signup_form():
    form = SignUpForm(data={
        'username': 'user1',
        'email': 'u1@example.com',
        'password1': 'Password1234',
        'password2': 'Password1234',
        'role': 'student'
    })
    assert form.is_valid()

@pytest.mark.django_db
def test_invalid_signup_password_mismatch():
    form = SignUpForm(data={
        'username': 'user2',
        'email': 'u2@example.com',
        'password1': 'pass1',
        'password2': 'pass2',
        'role': 'teacher'
    })
    assert not form.is_valid()

def test_course_form_valid():
    form = CourseForm(data={'name': 'Math', 'description': 'Nice course'})
    assert form.is_valid()

def test_course_form_empty():
    form = CourseForm(data={})
    assert not form.is_valid()

def test_question_form_valid():
    form = QuestionForm(data={
        'text': 'Test question?',
        'option1': 'A',
        'option2': 'B',
        'option3': 'C',
        'option4': 'D',
        'correct_option': 1,
        'marks': 5
    })
    assert form.is_valid()

def test_question_form_invalid_correct_option():
    form = QuestionForm(data={
        'text': 'Bad question',
        'option1': 'A',
        'option2': 'B',
        'option3': 'C',
        'option4': 'D',
        'correct_option': 7,  # Invalid
        'marks': 1
    })
    assert not form.is_valid()
