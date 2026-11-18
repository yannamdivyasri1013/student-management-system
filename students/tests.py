from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Student
from .views import ensure_default_admin


class StudentManagementTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True,
            is_superuser=True,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_admin_login_and_dashboard_access(self):
        login = self.client.login(username='admin', password='adminpass')
        self.assertTrue(login)

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_default_admin_is_created_when_missing(self):
        User = get_user_model()
        User.objects.filter(username='admin').delete()

        admin = ensure_default_admin()
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(self.client.login(username='admin', password='admin123'))

    def test_admin_registration(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newadmin',
                'email': 'newadmin@example.com',
                'password': 'newpass123',
                'confirm_password': 'newpass123',
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(username='newadmin').exists())

    def test_student_creation(self):
        self.client.login(username='admin', password='adminpass')
        payload = {
            'name': 'Alice Johnson',
            'roll_number': 'CS-101',
            'email': 'alice@example.com',
            'phone_number': '9876543210',
            'gender': 'Female',
            'date_of_birth': '2003-05-10',
            'department': 'Computer Science',
            'year': '2nd Year',
            'address': 'Boston, USA',
            'subject_name_1': 'Mathematics',
            'subject_name_2': 'Physics',
            'subject_name_3': 'Chemistry',
            'subject_name_4': 'English',
            'subject_name_5': 'Computer Science',
            'subject_1': 90,
            'subject_2': 84,
            'subject_3': 88,
            'subject_4': 81,
            'subject_5': 86,
        }
        response = self.client.post(reverse('add_student'), payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Student.objects.filter(roll_number='CS-101').exists())
        self.assertEqual(Student.objects.get(roll_number='CS-101').marks.subject_name_1, 'Mathematics')

    def test_student_filter_and_csv_export(self):
        self.client.login(username='admin', password='adminpass')
        Student.objects.create(
            name='Bob Smith', roll_number='IT-101', email='bob@example.com',
            phone_number='9876543210', gender='Male', date_of_birth='2003-01-15',
            department='Information Technology', year='2nd Year', address='New York',
        )

        response = self.client.get(reverse('student_list'), {'department': 'Information Technology'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bob Smith')

        csv_response = self.client.get(reverse('student_list'), {'export': 'csv'})
        self.assertEqual(csv_response.status_code, 200)
        self.assertEqual(csv_response['Content-Type'], 'text/csv')
        self.assertContains(csv_response, 'Bob Smith')
