from django.test import TestCase

from .models import User
from .serializers import UserCreateSerializer


class UserPhoneUniquenessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            phone='+254712345678',
            password='StrongPass123',
        )

    def test_duplicate_phone_is_rejected_even_with_different_format(self):
        serializer = UserCreateSerializer(
            data={
                'username': 'new_user',
                'phone': '0712345678',
                'password': 'StrongPass123',
                'first_name': 'New',
                'last_name': 'User',
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('phone', serializer.errors)
        self.assertIn('already exists', str(serializer.errors['phone'][0]))
