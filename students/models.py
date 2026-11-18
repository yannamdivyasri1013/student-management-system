from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    DEPARTMENT_CHOICES = [
        ('Computer Science', 'Computer Science'),
        ('Information Technology', 'Information Technology'),
        ('Electronics', 'Electronics'),
        ('Mechanical', 'Mechanical'),
        ('Civil', 'Civil'),
    ]

    YEAR_CHOICES = [
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
    ]

    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    year = models.CharField(max_length=20, choices=YEAR_CHOICES)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.roll_number})'

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class StudentMarks(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='marks')
    subject_name_1 = models.CharField(max_length=50, default='Subject 1')
    subject_name_2 = models.CharField(max_length=50, default='Subject 2')
    subject_name_3 = models.CharField(max_length=50, default='Subject 3')
    subject_name_4 = models.CharField(max_length=50, default='Subject 4')
    subject_name_5 = models.CharField(max_length=50, default='Subject 5')
    subject_1 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    subject_2 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    subject_3 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    subject_4 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    subject_5 = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    total = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    grade = models.CharField(max_length=2, default='F')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_result(self):
        values = [
            self.subject_1,
            self.subject_2,
            self.subject_3,
            self.subject_4,
            self.subject_5,
        ]
        total = sum(values)
        percentage = round((total / (len(values) * 100)) * 100, 2)

        if percentage >= 85:
            grade = 'A'
        elif percentage >= 70:
            grade = 'B'
        elif percentage >= 55:
            grade = 'C'
        elif percentage >= 40:
            grade = 'D'
        else:
            grade = 'F'

        return total, percentage, grade

    def save(self, *args, **kwargs):
        self.total, self.percentage, self.grade = self.calculate_result()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student.name} Marks'
