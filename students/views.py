from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import csv

from .forms import StudentForm, StudentMarksForm
from .models import Student, StudentMarks


def ensure_default_admin():
    User = get_user_model()
    admin_user = User.objects.filter(username='admin').first()

    if admin_user:
        if not admin_user.is_staff or not admin_user.is_superuser:
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save(update_fields=['is_staff', 'is_superuser'])
        return admin_user

    return User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')


def admin_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'Please fill in all required fields.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            User = get_user_model()
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, 'This username already exists. Please choose another one.')
            elif User.objects.filter(email__iexact=email).exists():
                messages.error(request, 'This email is already registered.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.is_staff = True
                user.is_superuser = False
                user.save(update_fields=['is_staff', 'is_superuser'])
                login(request, user)
                messages.success(request, 'Account created successfully. Welcome!')
                return redirect('dashboard')

    return render(request, 'register.html')


def admin_login(request):
    ensure_default_admin()

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active and (user.is_staff or user.is_superuser):
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password. Admin access is required.')

    return render(request, 'login.html')


def admin_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    total_students = Student.objects.count()
    recent_students = Student.objects.order_by('-created_at')[:5]
    gender_distribution = list(Student.objects.values('gender').annotate(count=Count('id')).order_by('gender'))
    department_distribution = list(Student.objects.values('department').annotate(count=Count('id')).order_by('department'))
    year_distribution = list(Student.objects.values('year').annotate(count=Count('id')).order_by('year'))

    context = {
        'total_students': total_students,
        'recent_students': recent_students,
        'gender_distribution': gender_distribution,
        'department_distribution': department_distribution,
        'year_distribution': year_distribution,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def student_list(request):
    query = request.GET.get('q', '').strip()
    department = request.GET.get('department', '').strip()
    year = request.GET.get('year', '').strip()
    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(name__icontains=query)
            | Q(roll_number__icontains=query)
            | Q(email__icontains=query)
        )
    if department:
        students = students.filter(department=department)
    if year:
        students = students.filter(year=year)

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Roll Number', 'Email', 'Phone', 'Gender', 'Department', 'Year'])
        for student in students:
            writer.writerow([
                student.name,
                student.roll_number,
                student.email,
                student.phone_number,
                student.gender,
                student.department,
                student.year,
            ])
        return response

    context = {
        'students': students,
        'query': query,
        'department': department,
        'year': year,
        'department_choices': Student.DEPARTMENT_CHOICES,
        'year_choices': Student.YEAR_CHOICES,
    }
    return render(request, 'student_list.html', context)


@login_required(login_url='login')
def add_student(request):
    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        marks_form = StudentMarksForm(request.POST)

        if student_form.is_valid() and marks_form.is_valid():
            student = student_form.save()
            marks = marks_form.save(commit=False)
            marks.student = student
            marks.save()
            messages.success(request, 'Student added successfully.')
            return redirect('student_list')
    else:
        student_form = StudentForm()
        marks_form = StudentMarksForm()

    context = {
        'student_form': student_form,
        'marks_form': marks_form,
        'title': 'Add Student',
        'button_text': 'Add Student',
    }
    return render(request, 'student_form.html', context)


@login_required(login_url='login')
def update_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    try:
        student_marks = student.marks
    except StudentMarks.DoesNotExist:
        student_marks = StudentMarks(student=student)

    if request.method == 'POST':
        student_form = StudentForm(request.POST, instance=student)
        marks_form = StudentMarksForm(request.POST, instance=student_marks)

        if student_form.is_valid() and marks_form.is_valid():
            student = student_form.save()
            marks = marks_form.save(commit=False)
            marks.student = student
            marks.save()
            messages.success(request, 'Student details updated successfully.')
            return redirect('student_profile', pk=student.pk)
    else:
        student_form = StudentForm(instance=student)
        marks_form = StudentMarksForm(instance=student_marks)

    context = {
        'student_form': student_form,
        'marks_form': marks_form,
        'student': student,
        'title': 'Update Student',
        'button_text': 'Save Changes',
    }
    return render(request, 'student_form.html', context)


@login_required(login_url='login')
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.delete()
        messages.success(request, f'{student.name} has been deleted successfully.')
        return redirect('student_list')

    return render(request, 'delete_student.html', {'student': student})


@login_required(login_url='login')
def student_profile(request, pk):
    student = get_object_or_404(Student, pk=pk)

    try:
        student_marks = student.marks
    except StudentMarks.DoesNotExist:
        student_marks = None

    context = {
        'student': student,
        'student_marks': student_marks,
    }
    return render(request, 'student_detail.html', context)


@login_required(login_url='login')
def marks_management(request, pk):
    student = get_object_or_404(Student, pk=pk)

    try:
        student_marks = student.marks
    except StudentMarks.DoesNotExist:
        student_marks = StudentMarks(student=student)

    if request.method == 'POST':
        form = StudentMarksForm(request.POST, instance=student_marks)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.student = student
            marks.save()
            messages.success(request, 'Marks updated successfully.')
            return redirect('student_profile', pk=student.pk)
    else:
        form = StudentMarksForm(instance=student_marks)

    context = {
        'student': student,
        'form': form,
    }
    return render(request, 'marks_form.html', context)


@login_required(login_url='login')
def export_students_csv(request):
    students = Student.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Roll Number', 'Email', 'Gender', 'Department', 'Year of Study'])

    for student in students:
        writer.writerow([
            student.id,
            student.name,
            student.roll_number,
            student.email,
            student.gender,
            student.department,
            student.year_of_study,
        ])

    messages.success(request, 'Students data exported successfully.')
    return response
