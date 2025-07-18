from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Newsletter, ContactMessage

class ContactForm(forms.ModelForm):
    """Contact form."""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your name')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your email')
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Subject')
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Your message'),
                'rows': 5
            })
        }

class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form."""
    
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your email')
            })
        }
    
    def clean_email(self):
        """Validate email."""
        email = self.cleaned_data['email']
        if Newsletter.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _('This email is already subscribed to our newsletter.')
            )
        return email
