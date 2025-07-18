from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from products.models import (
    Product, Brand, Category,
    FeaturedProduct, FeaturedBrand, FeaturedCategory
)
from .models import (
    Newsletter, 
    ContactMessage, 
    HeroBanner, 
    HomepageSettings
)
from .forms import ContactForm, NewsletterForm

class HomeView(TemplateView):
    """Home page view."""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get homepage settings
        settings = HomepageSettings.get_settings()
        context['homepage_settings'] = settings
        
        # Hero banners
        context['hero_banners'] = HeroBanner.objects.filter(is_active=True).order_by('order')
        
        # Deal of the Day products
        context['deal_products'] = self.get_featured_products('deal_of_day', settings.products_per_section)
        
        # Exclusive Brands
        context['exclusive_brands'] = self.get_featured_brands('exclusive_brands', settings.brands_per_section)
        
        # Top Picks
        context['top_picks'] = self.get_featured_products('top_picks', settings.products_per_section)
        
        # Shop by Category
        context['featured_categories'] = FeaturedCategory.objects.filter(
            is_active=True
        ).select_related('category').order_by('order')[:settings.categories_per_section]
        
        # Brand Deals
        context['brand_deals'] = self.get_featured_brands('brand_deals', settings.brands_per_section)
        
        # Trending Now
        context['trending_products'] = self.get_featured_products('trending_now', settings.products_per_section)
        
        # Indian Wear
        context['indian_wear_products'] = self.get_featured_products('indian_wear', settings.products_per_section)
        
        # Sports Wear
        context['sports_wear_products'] = self.get_featured_products('sports_wear', settings.products_per_section)
        
        # Footwear
        context['footwear_products'] = self.get_featured_products('footwear', settings.products_per_section)
        
        # New Brands
        context['new_brands'] = self.get_featured_brands('new_brands', settings.brands_per_section)
        
        return context
    
    def get_featured_products(self, section, limit):
        """Get featured products for a specific section."""
        now = timezone.now()
        featured_products = FeaturedProduct.objects.filter(
            section=section,
            is_active=True
        ).filter(
            models.Q(featured_until__isnull=True) | models.Q(featured_until__gt=now)
        ).select_related('product', 'product__brand').order_by('order')[:limit]
        
        return [fp.product for fp in featured_products]
    
    def get_featured_brands(self, section, limit):
        """Get featured brands for a specific section."""
        now = timezone.now()
        return FeaturedBrand.objects.filter(
            section=section,
            is_active=True
        ).filter(
            models.Q(featured_until__isnull=True) | models.Q(featured_until__gt=now)
        ).select_related('brand').order_by('order')[:limit]

class ContactView(FormView):
    """Contact form view."""
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')
    
    def form_valid(self, form):
        # Create contact message
        ContactMessage.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message']
        )
        messages.success(
            self.request,
            _('Thank you for your message. We will get back to you soon.')
        )
        return super().form_valid(form)

class NewsletterSubscribeView(FormView):
    """Newsletter subscription view."""
    form_class = NewsletterForm
    template_name = 'core/newsletter_subscribe.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        # Check if already subscribed
        if Newsletter.objects.filter(email=email).exists():
            messages.info(
                self.request,
                _('You are already subscribed to our newsletter.')
            )
        else:
            # Create new subscription
            Newsletter.objects.create(email=email)
            messages.success(
                self.request,
                _('Thank you for subscribing to our newsletter!')
            )
        return super().form_valid(form)

class NewsletterUnsubscribeView(FormView):
    """Newsletter unsubscribe view."""
    form_class = NewsletterForm
    template_name = 'core/newsletter_unsubscribe.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        # Try to find and delete subscription
        try:
            subscription = Newsletter.objects.get(email=email)
            subscription.delete()
            messages.success(
                self.request,
                _('You have been unsubscribed from our newsletter.')
            )
        except Newsletter.DoesNotExist:
            messages.error(
                self.request,
                _('This email address is not subscribed to our newsletter.')
            )
        return super().form_valid(form)
