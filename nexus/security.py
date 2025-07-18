from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, Optional, List, Union
from functools import wraps
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from .monitoring import Monitoring
from .cache import CacheService, RateLimiter

logger = logging.getLogger(__name__)
User = get_user_model()

class SecurityService:
    """Service class for handling security and authentication."""

    JWT_ALGORITHM = 'HS256'
    TOKEN_TYPE_ACCESS = 'access'
    TOKEN_TYPE_REFRESH = 'refresh'
    TOKEN_TYPE_RESET = 'reset'
    TOKEN_TYPE_VERIFY = 'verify'

    @classmethod
    def generate_token(
        cls,
        user_id: int,
        token_type: str = TOKEN_TYPE_ACCESS,
        expires_in: Optional[int] = None
    ) -> str:
        """Generate JWT token."""
        if expires_in is None:
            expires_in = {
                cls.TOKEN_TYPE_ACCESS: 3600,  # 1 hour
                cls.TOKEN_TYPE_REFRESH: 604800,  # 1 week
                cls.TOKEN_TYPE_RESET: 3600,  # 1 hour
                cls.TOKEN_TYPE_VERIFY: 86400,  # 24 hours
            }.get(token_type, 3600)

        payload = {
            'user_id': user_id,
            'type': token_type,
            'exp': timezone.now() + timedelta(seconds=expires_in),
            'iat': timezone.now(),
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=cls.JWT_ALGORITHM
        )

    @classmethod
    def verify_token(cls, token: str, token_type: str) -> Dict:
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[cls.JWT_ALGORITHM]
            )

            if payload['type'] != token_type:
                raise jwt.InvalidTokenError('Invalid token type')

            return payload

        except jwt.ExpiredSignatureError:
            raise PermissionDenied('Token has expired')
        except jwt.InvalidTokenError as e:
            raise PermissionDenied(f'Invalid token: {str(e)}')

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(
            password.encode(),
            hashed.encode()
        )

    @staticmethod
    def generate_password_reset_token(user: User) -> str:
        """Generate password reset token."""
        return SecurityService.generate_token(
            user.id,
            SecurityService.TOKEN_TYPE_RESET
        )

    @staticmethod
    def generate_email_verification_token(user: User) -> str:
        """Generate email verification token."""
        return SecurityService.generate_token(
            user.id,
            SecurityService.TOKEN_TYPE_VERIFY
        )

    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate password strength.
        
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        if not any(not c.isalnum() for c in password):
            return False
        return True

class AuthenticationService:
    """Service class for handling authentication."""

    @staticmethod
    @Monitoring.monitor_performance
    def authenticate(email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        try:
            user = User.objects.get(email=email)
            if SecurityService.verify_password(password, user.password):
                return user
            return None
        except User.DoesNotExist:
            return None

    @staticmethod
    def login(user: User) -> Dict[str, str]:
        """Generate access and refresh tokens for user."""
        access_token = SecurityService.generate_token(
            user.id,
            SecurityService.TOKEN_TYPE_ACCESS
        )
        refresh_token = SecurityService.generate_token(
            user.id,
            SecurityService.TOKEN_TYPE_REFRESH
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

    @staticmethod
    def refresh_token(refresh_token: str) -> str:
        """Generate new access token using refresh token."""
        payload = SecurityService.verify_token(
            refresh_token,
            SecurityService.TOKEN_TYPE_REFRESH
        )
        return SecurityService.generate_token(
            payload['user_id'],
            SecurityService.TOKEN_TYPE_ACCESS
        )

    @staticmethod
    def logout(user: User) -> None:
        """Handle user logout."""
        # Invalidate user sessions
        from django.contrib.sessions.models import Session
        Session.objects.filter(
            expire_date__gte=timezone.now(),
            session_data__contains=str(user.id)
        ).delete()

class AuthorizationService:
    """Service class for handling authorization."""

    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        """Check if user has specific permission."""
        return user.has_perm(permission)

    @staticmethod
    def has_role(user: User, role: str) -> bool:
        """Check if user has specific role."""
        return user.groups.filter(name=role).exists()

    @staticmethod
    def require_permission(permission: str):
        """Decorator to require specific permission."""
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                if not request.user.has_perm(permission):
                    raise PermissionDenied(
                        f'Permission required: {permission}'
                    )
                return func(request, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def require_role(role: str):
        """Decorator to require specific role."""
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                if not AuthorizationService.has_role(request.user, role):
                    raise PermissionDenied(
                        f'Role required: {role}'
                    )
                return func(request, *args, **kwargs)
            return wrapper
        return decorator

class SecurityMiddleware:
    """Middleware for handling security concerns."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rate limiting
        if not self._check_rate_limit(request):
            raise PermissionDenied('Rate limit exceeded')

        # Security headers
        response = self.get_response(request)
        self._add_security_headers(response)

        return response

    def _check_rate_limit(self, request) -> bool:
        """Check rate limiting for request."""
        if request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
        else:
            identifier = f"ip:{request.META.get('REMOTE_ADDR')}"

        return RateLimiter.check_rate_limit(
            identifier=identifier,
            action='api_request',
            max_requests=100,
            time_window=3600
        )

    def _add_security_headers(self, response):
        """Add security headers to response."""
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = self._get_csp_policy()
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Feature-Policy'] = self._get_feature_policy()

    def _get_csp_policy(self) -> str:
        """Get Content Security Policy."""
        return "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "img-src 'self' data: https:",
            "font-src 'self' https://fonts.gstatic.com",
            "connect-src 'self' https://api.stripe.com",
            "frame-src 'self' https://js.stripe.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "block-all-mixed-content",
            "upgrade-insecure-requests"
        ])

    def _get_feature_policy(self) -> str:
        """Get Feature Policy."""
        return "; ".join([
            "geolocation 'none'",
            "midi 'none'",
            "notifications 'none'",
            "push 'none'",
            "sync-xhr 'none'",
            "microphone 'none'",
            "camera 'none'",
            "magnetometer 'none'",
            "gyroscope 'none'",
            "speaker 'none'",
            "vibrate 'none'",
            "fullscreen 'self'",
            "payment 'self'"
        ])

class TwoFactorAuthService:
    """Service class for handling 2FA."""

    @staticmethod
    def generate_2fa_token(user: User) -> str:
        """Generate 2FA token."""
        import pyotp
        return pyotp.random_base32()

    @staticmethod
    def verify_2fa_token(user: User, token: str) -> bool:
        """Verify 2FA token."""
        import pyotp
        totp = pyotp.TOTP(user.two_factor_secret)
        return totp.verify(token)

    @staticmethod
    def get_2fa_qr_code(user: User) -> str:
        """Get QR code for 2FA setup."""
        import pyotp
        import qrcode
        import io
        import base64

        totp = pyotp.TOTP(user.two_factor_secret)
        uri = totp.provisioning_uri(
            user.email,
            issuer_name="NEXUS Fashion"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
