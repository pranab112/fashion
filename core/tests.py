from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import (
    SiteConfiguration,
    Banner,
    Newsletter,
    ContactMessage,
    FAQ,
    Testimonial,
    SocialProof
)
from .forms import (
    NewsletterForm,
    ContactForm,
    SearchForm,
    FeedbackForm,
    SizeGuideForm
)

User = get_user_model()

class CoreModelsTest(TestCase):
    """Test cases for core models."""

    def setUp(self):
        self.site_config = SiteConfiguration.objects.create(
            site_name="Test Site",
            contact_email="test@example.com"
        )
        self.banner = Banner.objects.create(
            title="Test Banner",
            image="banners/test.jpg",
            is_active=True
        )
        self.newsletter = Newsletter.objects.create(
            email="subscriber@example.com"
        )

    def test_site_configuration_str(self):
        """Test SiteConfiguration string representation."""
        self.assertEqual(str(self.site_config), "Test Site")

    def test_single_site_configuration(self):
        """Test that only one site configuration can exist."""
        new_config = SiteConfiguration.objects.create(
            site_name="Another Site",
            contact_email="another@example.com"
        )
        self.assertEqual(SiteConfiguration.objects.count(), 1)
        self.assertEqual(SiteConfiguration.objects.first().site_name, "Test Site")

    def test_banner_str(self):
        """Test Banner string representation."""
        self.assertEqual(str(self.banner), "Test Banner")

    def test_newsletter_str(self):
        """Test Newsletter string representation."""
        self.assertEqual(str(self.newsletter), "subscriber@example.com")

class CoreFormsTest(TestCase):
    """Test cases for core forms."""

    def test_newsletter_subscription_form_valid(self):
        """Test newsletter subscription form with valid data."""
        form = NewsletterForm({
            'email': 'test@example.com'
        })
        self.assertTrue(form.is_valid())

    def test_newsletter_subscription_form_invalid(self):
        """Test newsletter subscription form with invalid data."""
        form = NewsletterSubscriptionForm({
            'email': 'invalid-email'
        })
        self.assertFalse(form.is_valid())

    def test_contact_form_valid(self):
        """Test contact form with valid data."""
        form = ContactForm({
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test Message'
        })
        self.assertTrue(form.is_valid())

    def test_search_form_valid(self):
        """Test search form with valid data."""
        form = SearchForm({
            'q': 'test query',
            'min_price': '10',
            'max_price': '100'
        })
        self.assertTrue(form.is_valid())

class CoreViewsTest(TestCase):
    """Test cases for core views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_home_view(self):
        """Test homepage view."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_about_view(self):
        """Test about page view."""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/about.html')

    def test_contact_view(self):
        """Test contact page view and form submission."""
        # Test GET request
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contact.html')

        # Test POST request
        response = self.client.post(reverse('core:contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test Message'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(len(mail.outbox), 1)  # Email sent
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_newsletter_subscribe(self):
        """Test newsletter subscription endpoint."""
        response = self.client.post(reverse('core:newsletter_subscribe'), {
            'email': 'subscriber@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Newsletter.objects.count(), 1)

    def test_maintenance_mode(self):
        """Test maintenance mode page."""
        config = SiteConfiguration.objects.create(
            site_name="Test Site",
            contact_email="test@example.com",
            maintenance_mode=True,
        )
        response = self.client.get(reverse('core:maintenance'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/maintenance.html')
        self.assertContains(response, "Under maintenance")

class CoreIntegrationTest(TestCase):
    """Integration tests for core functionality."""

    def setUp(self):
        self.client = Client()
        self.site_config = SiteConfiguration.objects.create(
            site_name="Test Site",
            contact_email="test@example.com"
        )

    def test_search_functionality(self):
        """Test search functionality with filters."""
        response = self.client.get(reverse('core:search'), {
            'q': 'test',
            'min_price': '10',
            'max_price': '100',
            'sort': 'price_asc'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/search.html')

    def test_size_guide_calculator(self):
        """Test size guide calculator functionality."""
        response = self.client.post(reverse('core:size_guide'), {
            'gender': 'M',
            'height': '180',
            'weight': '75'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('size', response.json())

    def test_feedback_submission(self):
        """Test feedback submission functionality."""
        response = self.client.post(reverse('core:submit_feedback'), {
            'rating': '5',
            'comment': 'Great service!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
