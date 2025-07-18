from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ..models import Address
from ..serializers import (
    UserSerializer,
    AddressSerializer,
    UserCreateSerializer,
    PasswordChangeSerializer
)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""
    
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter queryset to return only the requesting user."""
        return self.queryset.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password."""
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                return Response(
                    {'message': _('Password updated successfully.')},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'error': _('Incorrect old password.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for Address model."""
    
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to return only addresses belonging to the requesting user."""
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user when creating a new address."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set an address as default."""
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response(
            {'message': _('Address set as default successfully.')},
            status=status.HTTP_200_OK
        )
