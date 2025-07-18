from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Profile, Address, Newsletter, ContactMessage

User = get_user_model()

class UserModelTest(TestCase):
    """Test cases for User model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_profile_creation(self):
        """Test profile auto-creation."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsNotNone(self.user.profile)

class ProfileModelTest(TestCase):
    """Test cases for Profile model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile
        self.profile.phone_number = '1234567890'
        self.profile.gender = 'M'
        self.profile.save()

    def test_profile_creation(self):
        """Test profile creation."""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.phone_number, '1234567890')
        self.assertEqual(self.profile.gender, 'M')

    def test_profile_str_representation(self):
        """Test profile string representation."""
        expected = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.profile), expected)

    def test_profile_update(self):
        """Test profile update."""
        self.profile.phone_number = '0987654321'
        self.profile.save()
        self.assertEqual(self.profile.phone_number, '0987654321')

class AddressModelTest(TestCase):
    """Test cases for Address model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.address = Address.objects.create(
            user=self.user,
            address_type='home',
            full_name='Test User',
            phone_number='1234567890',
            street_address1='123 Test St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            is_default=True
        )

    def test_address_creation(self):
        """Test address creation."""
        self.assertEqual(self.address.user, self.user)
        self.assertEqual(self.address.address_type, 'home')
        self.assertTrue(self.address.is_default)

    def test_address_str_representation(self):
        """Test address string representation."""
        expected = f"{self.user.username}'s home Address"
        self.assertEqual(str(self.address), expected)

    def test_default_address_logic(self):
        """Test default address logic."""
        # Create another address
        new_address = Address.objects.create(
            user=self.user,
            address_type='work',
            full_name='Test User',
            phone='0987654321',
            street_address='456 Work St',
            city='Test City',
            state='Test State',
            postal_code='54321',
            is_default=True
        )
        
        # Check that old address is no longer default
        self.address.refresh_from_db()
        self.assertFalse(self.address.is_default)
        self.assertTrue(new_address.is_default)

class NewsletterModelTest(TestCase):
    """Test cases for Newsletter model."""

    def setUp(self):
        self.newsletter = Newsletter.objects.create(
            email='test@example.com'
        )

    def test_newsletter_creation(self):
        """Test newsletter subscription creation."""
        self.assertEqual(self.newsletter.email, 'test@example.com')
        self.assertTrue(self.newsletter.is_active)

    def test_newsletter_str_representation(self):
        """Test newsletter string representation."""
        self.assertEqual(str(self.newsletter), 'test@example.com')

    def test_unique_email_constraint(self):
        """Test unique email constraint."""
        with self.assertRaises(Exception):
            Newsletter.objects.create(email='test@example.com')

class ContactMessageModelTest(TestCase):
    """Test cases for ContactMessage model."""

    def setUp(self):
        self.message = ContactMessage.objects.create(
            name='Test User',
            email='test@example.com',
            subject='Test Subject',
            message='Test Message'
        )

    def test_message_creation(self):
        """Test contact message creation."""
        self.assertEqual(self.message.name, 'Test User')
        self.assertEqual(self.message.email, 'test@example.com')
        self.assertFalse(self.message.is_read)

    def test_message_str_representation(self):
        """Test message string representation."""
        expected = f"Message from Test User - Test Subject"
        self.assertEqual(str(self.message), expected)

class UserViewTest(TestCase):
    """Test cases for user views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_url = reverse('users:login')
        self.register_url = reverse('users:register')
        self.profile_url = reverse('users:profile')

    def test_login_view(self):
        """Test login view."""
        # Test GET request
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

        # Test successful login
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_register_view(self):
        """Test register view."""
        # Test GET request
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

        # Test successful registration
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_view(self):
        """Test profile view."""
        # Login required
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

        # Test after login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_update(self):
        """Test profile update."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.profile_url, {
            'first_name': 'Updated',
            'last_name': 'User',
            'phone_number': '1234567890'
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

class AddressViewTest(TestCase):
    """Test cases for address views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.address_data = {
            'address_type': 'home',
            'full_name': 'Test User',
            'phone_number': '1234567890',
            'street_address1': '123 Test St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345'
        }

    def test_address_list_view(self):
        """Test address list view."""
        response = self.client.get(reverse('users:addresses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/address_list.html')

    def test_address_create_view(self):
        """Test address creation view."""
        response = self.client.post(
            reverse('users:address_create'),
            self.address_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Address.objects.filter(user=self.user).exists()
        )

    def test_address_update_view(self):
        """Test address update view."""
        address = Address.objects.create(user=self.user, **self.address_data)
        response = self.client.post(
            reverse('users:address_update', kwargs={'pk': address.pk}),
            {**self.address_data, 'city': 'New City'}
        )
        self.assertEqual(response.status_code, 302)
        address.refresh_from_db()
        self.assertEqual(address.city, 'New City')

class NewsletterViewTest(TestCase):
    """Test cases for newsletter views."""

    def setUp(self):
        self.client = Client()

    def test_newsletter_subscription(self):
        """Test newsletter subscription."""
        response = self.client.post(
            reverse('users:newsletter_subscribe'),
            {'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Newsletter.objects.filter(email='test@example.com').exists()
        )

class ContactViewTest(TestCase):
    """Test cases for contact views."""

    def setUp(self):
        self.client = Client()
        self.contact_url = reverse('users:contact')

    def test_contact_view(self):
        """Test contact form view."""
        # Test GET request
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/contact.html')

        # Test form submission
        response = self.client.post(self.contact_url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test Message'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ContactMessage.objects.filter(email='test@example.com').exists()
        )
