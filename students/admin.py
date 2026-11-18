from django.contrib import admin

from .models import Student, StudentMarks


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'department', 'year')
    search_fields = ('name', 'roll_number', 'email')


@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'total', 'percentage', 'grade')
    search_fields = ('student__name', 'student__roll_number')
