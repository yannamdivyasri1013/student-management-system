from django import forms
from django.utils import timezone

from .models import Student, StudentMarks


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name',
            'roll_number',
            'email',
            'phone_number',
            'gender',
            'date_of_birth',
            'department',
            'year',
            'address',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter roll number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter address'}),
        }

    def clean_roll_number(self):
        roll_number = self.cleaned_data['roll_number'].strip()
        if Student.objects.filter(roll_number__iexact=roll_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This roll number already exists. Please use a unique roll number.')
        return roll_number

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if Student.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number'].strip()
        if not phone_number.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        if len(phone_number) < 10 or len(phone_number) > 15:
            raise forms.ValidationError('Phone number must be between 10 and 15 digits.')
        return phone_number

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data['date_of_birth']
        if date_of_birth and date_of_birth > timezone.now().date():
            raise forms.ValidationError('Date of birth cannot be in the future.')
        return date_of_birth


class StudentMarksForm(forms.ModelForm):
    class Meta:
        model = StudentMarks
        fields = [
            'subject_name_1',
            'subject_1',
            'subject_name_2',
            'subject_2',
            'subject_name_3',
            'subject_3',
            'subject_name_4',
            'subject_4',
            'subject_name_5',
            'subject_5',
        ]
        widgets = {
            'subject_name_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Mathematics'}),
            'subject_1': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'subject_name_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Physics'}),
            'subject_2': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'subject_name_3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Chemistry'}),
            'subject_3': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'subject_name_4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. English'}),
            'subject_4': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'subject_name_5': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science'}),
            'subject_5': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

    @property
    def subject_fields(self):
        return [
            {'name': self['subject_name_1'], 'mark': self['subject_1']},
            {'name': self['subject_name_2'], 'mark': self['subject_2']},
            {'name': self['subject_name_3'], 'mark': self['subject_3']},
            {'name': self['subject_name_4'], 'mark': self['subject_4']},
            {'name': self['subject_name_5'], 'mark': self['subject_5']},
        ]

    def clean(self):
        cleaned_data = super().clean()
        values = [
            cleaned_data.get('subject_1', 0),
            cleaned_data.get('subject_2', 0),
            cleaned_data.get('subject_3', 0),
            cleaned_data.get('subject_4', 0),
            cleaned_data.get('subject_5', 0),
        ]

        for value in values:
            if value < 0 or value > 100:
                raise forms.ValidationError('Each subject mark must be between 0 and 100.')

        return cleaned_data
