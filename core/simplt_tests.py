"""
Simple tests to debug issues
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse

class SimpleAuthTests(TestCase):
    def setUp(self):
        # Simple setup without transactions
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
    
    def test_login_works(self):
        """Simple login test"""
        response = self.client.get(reverse('login'))
        print(f"Login page status: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_logout_requires_post(self):
        """Test logout method"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Try GET (should fail)
        response = self.client.get(reverse('logout'))
        print(f"GET logout status: {response.status_code}")
        
        # Try POST (should work)
        response = self.client.post(reverse('logout'))
        print(f"POST logout status: {response.status_code}")
        self.assertEqual(response.status_code, 302)