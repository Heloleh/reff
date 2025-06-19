from django.contrib.admin.sites import site
from core.models import Course, Question, ExamAttempt, Teacher

def test_models_registered_in_admin():
    assert Course in site._registry
    assert Question in site._registry
    assert ExamAttempt in site._registry
    assert Teacher in site._registry
