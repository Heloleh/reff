from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, CourseForm, QuestionForm
from .models import Teacher, Course, Question, ExamAttempt
from django.contrib.auth.models import User
import random

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            if role == 'teacher':
                Teacher.objects.create(user=user, is_approved=False)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required
def student_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not (request.user.is_superuser or (hasattr(request.user, 'teacher') and request.user.teacher.is_approved)):
        messages.error(request, 'You are not authorized to view student progress.')
        return redirect('dashboard')

    attempts = ExamAttempt.objects.filter(course=course).select_related('student')
    students_progress = {}
    for attempt in attempts:
        if attempt.student not in students_progress:
            students_progress[attempt.student] = {'total_score': 0, 'max_score': 0, 'attempts': 0}
        students_progress[attempt.student]['total_score'] += attempt.score
        students_progress[attempt.student]['max_score'] += sum(q.marks for q in attempt.course.questions.all())
        students_progress[attempt.student]['attempts'] += 1
        # Оновлюємо прогрес як середній відсоток
        attempt.progress_percentage = (students_progress[attempt.student]['total_score'] / students_progress[attempt.student]['max_score'] * 100) if students_progress[attempt.student]['max_score'] > 0 else 0
        attempt.save()

    context = {
        'course': course,
        'students_progress': students_progress,
    }
    return render(request, 'core/student_progress.html', context)

@login_required
def dashboard(request):
    if request.user.is_superuser:
        context = {
            'student_count': User.objects.filter(teacher__isnull=True, is_superuser=False).count(),
            'teacher_count': Teacher.objects.count(),
            'course_count': Course.objects.count(),
            'question_count': Question.objects.count(),
        }
        return render(request, 'core/admin_dashboard.html', context)
    elif hasattr(request.user, 'teacher'):
        if not request.user.teacher.is_approved:
            messages.warning(request, 'Your teacher account is awaiting admin approval.')
        context = {
            'student_count': User.objects.filter(teacher__isnull=True, is_superuser=False).count(),
            'course_count': Course.objects.count(),
            'question_count': Question.objects.count(),
            'is_approved': request.user.teacher.is_approved,
        }
        return render(request, 'core/teacher_dashboard.html', context)
    else:
        context = {
            'course_count': Course.objects.count(),
            'question_count': Question.objects.count(),
            'attempts': ExamAttempt.objects.filter(student=request.user),
        }
        return render(request, 'core/student_dashboard.html', context)

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'core/course_list.html', {'courses': courses})

@login_required
def create_course(request):
    if request.user.is_superuser or (hasattr(request.user, 'teacher') and request.user.teacher.is_approved):
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save(commit=False)
                course.created_by = request.user
                course.save()
                messages.success(request, 'Course created successfully!')
                return redirect('course_list')
        else:
            form = CourseForm()
        return render(request, 'core/course_form.html', {'form': form})
    messages.error(request, 'You are not authorized to create courses.')
    return redirect('dashboard')

@login_required
def create_question(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.is_superuser or (hasattr(request.user, 'teacher') and request.user.teacher.is_approved):
        if request.method == 'POST':
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.course = course
                question.save()
                messages.success(request, 'Question added successfully!')
                return redirect('question_list', course_id=course.id)
        else:
            form = QuestionForm()
        return render(request, 'core/question_form.html', {'form': form, 'course': course})
    messages.error(request, 'You are not authorized to add questions.')
    return redirect('dashboard')

@login_required
def question_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = Question.objects.filter(course=course)
    return render(request, 'core/question_list.html', {'course': course, 'questions': questions})

@login_required
def take_exam(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.is_superuser or (hasattr(request.user, 'teacher') and request.user.teacher.is_approved):
        messages.error(request, 'Only students can take the exam.')
        return redirect('dashboard')

    # Перевірка, чи студент уже проходив тест
    if ExamAttempt.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'You have already taken this exam.')
        return redirect('dashboard')

    if request.method == 'POST':
        score = 0
        questions = course.questions.all()
        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if selected_option and int(selected_option) == question.correct_option:
                score += question.marks
        ExamAttempt.objects.create(student=request.user, course=course, score=score)
        messages.success(request, f'Exam completed! Your score: {score}/{sum(q.marks for q in questions)}')
        return redirect('results', course_id=course.id)

    questions = list(course.questions.all())
    random.shuffle(questions)
    context = {'course': course, 'questions': questions}
    return render(request, 'core/take_exam.html', context)

@login_required
def results(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    attempts = ExamAttempt.objects.filter(student=request.user, course=course)
    return render(request, 'core/results.html', {'course': course, 'attempts': attempts})

@login_required
def teacher_management(request):
    if request.user.is_superuser:
        teachers = Teacher.objects.all()
        if request.method == 'POST':
            teacher_id = request.POST.get('teacher_id')
            action = request.POST.get('action')
            teacher = get_object_or_404(Teacher, id=teacher_id)
            if action == 'approve':
                teacher.is_approved = True
                teacher.save()
                messages.success(request, f'{teacher.user.username} approved.')
            elif action == 'delete':
                teacher.user.delete()
                messages.success(request, f'{teacher.user.username} deleted.')
            return redirect('teacher_management')
        return render(request, 'core/teacher_management.html', {'teachers': teachers})
    messages.error(request, 'You are not authorized to manage teachers.')
    return redirect('dashboard')

@login_required
def student_management(request):
    if request.user.is_superuser:
        students = User.objects.filter(teacher__isnull=True, is_superuser=False)
        if request.method == 'POST':
            student_id = request.POST.get('student_id')
            student = get_object_or_404(User, id=student_id)
            student.delete()
            messages.success(request, f'{student.username} deleted.')
            return redirect('student_management')
        return render(request, 'core/student_management.html', {'students': students})
    messages.error(request, 'You are not authorized to manage students.')
    return redirect('dashboard')