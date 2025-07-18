# Quick Start Guide

This guide will help you get the NEXUS Fashion Store up and running quickly for development.

## Prerequisites

1. Python 3.8 or higher
2. pip (Python package installer)
3. Git
4. Virtual environment tool (venv, virtualenv, or similar)

## Setup Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd clothing-brand
```

### 2. Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 4. Environment Setup

Create a `.env` file in the project root with these settings:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Optional settings
REDIS_URL=redis://localhost:6379/0
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 6. Static Files

```bash
# Collect static files
python manage.py collectstatic
```

### 7. Start Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser.

Admin interface is at http://127.0.0.1:8000/admin/

## Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
git add .
git commit -m "Description of your changes"
```

3. Run tests:
```bash
python manage.py test
```

4. Push your changes:
```bash
git push origin feature/your-feature-name
```

## Common Tasks

### Creating New Apps

```bash
python manage.py startapp appname
```

Add the app to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    ...
    'appname',
]
```

### Database Operations

```bash
# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Working with Templates

Templates are in the `templates` directory, organized by app:
```
templates/
    base.html
    core/
        home.html
        about.html
    products/
        list.html
        detail.html
    cart/
        cart.html
    users/
        profile.html
```

### Static Files

Static files are in the `static` directory:
```
static/
    css/
        style.css
    js/
        main.js
    images/
```

### Running Background Tasks

```bash
# Start Celery worker
celery -A nexus worker -l info

# Start Celery beat (for periodic tasks)
celery -A nexus beat -l info
```

## Troubleshooting

### Common Issues

1. **Database migrations conflicts**
   ```bash
   python manage.py migrate --fake
   python manage.py migrate
   ```

2. **Static files not showing**
   ```bash
   python manage.py collectstatic --clear
   python manage.py collectstatic
   ```

3. **Redis connection issues**
   - Check if Redis is running
   - Verify Redis URL in settings

4. **Permission issues with media uploads**
   - Check directory permissions
   - Verify media root settings

### Getting Help

1. Check the project documentation
2. Look for similar issues in the issue tracker
3. Ask in the project's communication channels
4. Contact the maintainers

## Next Steps

- Review the full documentation
- Explore the API documentation
- Check the deployment guide
- Read the contributing guidelines

## Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Tailwind CSS Documentation: https://tailwindcss.com/docs
- Celery Documentation: https://docs.celeryproject.org/
- Redis Documentation: https://redis.io/documentation
