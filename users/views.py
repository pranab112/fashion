from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Address
from .forms import (
    CustomUserCreationForm,
    UserProfileForm,
    AddressForm
)

class RegisterView(CreateView):
    """View for user registration."""
    
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        """Log the user in after successful registration."""
        try:
            response = super().form_valid(form)
            login(self.request, self.object)
            messages.success(
                self.request,
                _('Registration successful. Welcome to our store!')
            )
            return response
        except Exception as e:
            messages.error(
                self.request,
                _('Registration failed. Please try again with a different email.')
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(
            self.request,
            _('Please correct the errors below.')
        )
        return super().form_invalid(form)

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    """View for updating user profile."""
    
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, _('Profile updated successfully!'))
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class AddressListView(ListView):
    """View for listing user addresses."""
    
    model = Address
    template_name = 'users/address_list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

@method_decorator(login_required, name='dispatch')
class AddressCreateView(CreateView):
    """View for creating a new address."""
    
    model = Address
    form_class = AddressForm
    template_name = 'users/address_form.html'
    success_url = reverse_lazy('users:address_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, _('Address added successfully!'))
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class AddressUpdateView(UpdateView):
    """View for updating an address."""
    
    model = Address
    form_class = AddressForm
    template_name = 'users/address_form.html'
    success_url = reverse_lazy('users:address_list')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, _('Address updated successfully!'))
        return super().form_valid(form)

@login_required
def address_delete(request, pk):
    """View for deleting an address."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, _('Address deleted successfully!'))
    return redirect('users:address_list')

@login_required
def set_default_address(request, pk):
    """View for setting an address as default."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, _('Default address updated successfully!'))
    return redirect('users:address_list')
