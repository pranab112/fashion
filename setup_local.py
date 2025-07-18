#!/usr/bin/env python
"""
Local development environment setup script for the Nexus Fashion Store project.
Sets up everything needed for local development, including:
- Virtual environment
- Dependencies
- Database
- Sample data
- Pre-commit hooks
"""

import os
import platform
import subprocess
import sys
import venv
from pathlib import Path
from typing import List, Optional

class LocalSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.python_path = self.venv_path / ("Scripts" if platform.system() == "Windows" else "bin")
        self.pip = str(self.python_path / "pip")
        self.python = str(self.python_path / "python")

    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> None:
        """Run a command and handle errors."""
        try:
            subprocess.run(command, check=True, cwd=cwd)
        except subprocess.CalledProcessError as e:
            print(f"Error running command {' '.join(command)}: {e}")
            sys.exit(1)

    def create_virtual_environment(self) -> None:
        """Create a virtual environment if it doesn't exist."""
        print("\n📦 Creating virtual environment...")
        if not self.venv_path.exists():
            venv.create(self.venv_path, with_pip=True)
            print("✅ Virtual environment created successfully")
        else:
            print("ℹ️ Virtual environment already exists")

    def install_dependencies(self) -> None:
        """Install Python dependencies."""
        print("\n📥 Installing dependencies...")
        
        # Install pip-tools
        self.run_command([self.pip, "install", "pip-tools"])
        
        # Compile requirements if needed
        if not (self.project_root / "requirements.txt").exists():
            if (self.project_root / "requirements.in").exists():
                self.run_command([
                    str(self.python_path / "pip-compile"),
                    "requirements.in"
                ])
        
        # Install requirements
        self.run_command([self.pip, "install", "-r", "requirements.txt"])
        if (self.project_root / "requirements-local.txt").exists():
            self.run_command([self.pip, "install", "-r", "requirements-local.txt"])
        
        print("✅ Dependencies installed successfully")

    def setup_pre_commit(self) -> None:
        """Set up pre-commit hooks."""
        print("\n🔧 Setting up pre-commit hooks...")
        self.run_command([self.pip, "install", "pre-commit"])
        self.run_command([str(self.python_path / "pre-commit"), "install"])
        self.run_command([str(self.python_path / "pre-commit"), "install", "--hook-type", "pre-push"])
        print("✅ Pre-commit hooks installed successfully")

    def setup_database(self) -> None:
        """Set up the database."""
        print("\n🗄️ Setting up database...")
        self.run_command([self.python, "manage.py", "migrate"])
        print("✅ Database migrations applied successfully")

    def create_superuser(self) -> None:
        """Create a superuser if one doesn't exist."""
        print("\n👤 Creating superuser...")
        env = os.environ.copy()
        env["DJANGO_SUPERUSER_USERNAME"] = "admin"
        env["DJANGO_SUPERUSER_EMAIL"] = "admin@example.com"
        env["DJANGO_SUPERUSER_PASSWORD"] = "admin"
        
        try:
            self.run_command(
                [self.python, "manage.py", "createsuperuser", "--noinput"],
                env=env
            )
            print("✅ Superuser created successfully")
        except subprocess.CalledProcessError:
            print("ℹ️ Superuser already exists")

    def load_sample_data(self) -> None:
        """Load sample data."""
        print("\n📊 Loading sample data...")
        if (self.project_root / "fixtures" / "sample_data.json").exists():
            self.run_command([self.python, "manage.py", "loaddata", "fixtures/sample_data.json"])
            print("✅ Sample data loaded successfully")
        else:
            print("ℹ️ No sample data found")

    def collect_static(self) -> None:
        """Collect static files."""
        print("\n📁 Collecting static files...")
        self.run_command([self.python, "manage.py", "collectstatic", "--noinput"])
        print("✅ Static files collected successfully")

    def setup_redis(self) -> None:
        """Check Redis installation."""
        print("\n📊 Checking Redis installation...")
        try:
            import redis
            client = redis.Redis(host='localhost', port=6379, db=0)
            client.ping()
            print("✅ Redis is running")
        except (ImportError, redis.ConnectionError):
            print("⚠️ Redis is not available. Some features may not work properly.")
            print("Please install and start Redis server:")
            if platform.system() == "Windows":
                print("Download from: https://github.com/microsoftarchive/redis/releases")
            elif platform.system() == "Darwin":
                print("Run: brew install redis && brew services start redis")
            else:
                print("Run: sudo apt-get install redis-server")

    def setup_development_tools(self) -> None:
        """Install and configure development tools."""
        print("\n🛠️ Setting up development tools...")
        
        # Install development dependencies
        dev_packages = [
            "ipython",
            "django-debug-toolbar",
            "django-extensions",
            "werkzeug",
            "pytest-watch",
            "coverage",
        ]
        self.run_command([self.pip, "install"] + dev_packages)
        
        print("✅ Development tools installed successfully")

    def create_env_file(self) -> None:
        """Create .env file if it doesn't exist."""
        print("\n📝 Creating .env file...")
        env_file = self.project_root / ".env"
        if not env_file.exists():
            env_content = """
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Redis settings (optional)
REDIS_URL=redis://localhost:6379/0

# AWS settings (optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Stripe settings (optional)
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
            """.strip()
            env_file.write_text(env_content)
            print("✅ .env file created successfully")
        else:
            print("ℹ️ .env file already exists")

    def print_success_message(self) -> None:
        """Print success message with next steps."""
        print("""
🎉 Local development environment setup complete!

Next steps:
1. Activate the virtual environment:
   - Windows: .\\venv\\Scripts\\activate
   - Unix/MacOS: source venv/bin/activate

2. Start the development server:
   python manage.py runserver

3. Visit the site at:
   http://localhost:8000/

4. Access the admin interface at:
   http://localhost:8000/admin/
   Username: admin
   Password: admin

Happy coding! 🚀
        """)

    def setup(self) -> None:
        """Run the complete setup process."""
        print("🚀 Setting up Nexus Fashion Store development environment...")
        
        self.create_virtual_environment()
        self.install_dependencies()
        self.setup_pre_commit()
        self.create_env_file()
        self.setup_database()
        self.create_superuser()
        self.load_sample_data()
        self.collect_static()
        self.setup_redis()
        self.setup_development_tools()
        self.print_success_message()


if __name__ == "__main__":
    setup = LocalSetup()
    setup.setup()
