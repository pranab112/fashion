from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.views.static import serve
from django.http import HttpResponse
import os
from . import views

app_name = 'core'

def serve_service_worker(request):
    """Serve the service worker from static files."""
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'service-worker.js')
    try:
        with open(sw_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='application/javascript')
    except FileNotFoundError:
        return HttpResponse('// Service worker not found', content_type='application/javascript', status=404)

def serve_manifest(request):
    """Serve the manifest from static files."""
    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='application/json')
    except FileNotFoundError:
        return HttpResponse('{}', content_type='application/json', status=404)

urlpatterns = [
    # Home page
    path('', views.HomeView.as_view(), name='home'),
    
    # Static pages
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('blog/', TemplateView.as_view(template_name='core/blog.html'), name='blog'),
    
    # Newsletter subscription
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter_unsubscribe'),
    
    # Service worker and manifest
    path('sw.js', serve_service_worker, name='service_worker'),
    path('manifest.json', serve_manifest, name='manifest'),
    
    # Offline page
    path('offline/', TemplateView.as_view(template_name='core/offline.html'), name='offline'),
]
