#!/usr/bin/env python
"""
Local test runner for the Nexus Fashion Store project.
Provides a streamlined interface for running tests during development.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

class LocalTestRunner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_dirs = {
            'core': 'core/tests',
            'products': 'products/tests',
            'cart': 'cart/tests',
            'users': 'users/tests',
        }

    def run_tests(
        self,
        app: Optional[str] = None,
        test_path: Optional[str] = None,
        watch: bool = False,
        coverage: bool = False,
        verbose: bool = False,
        failfast: bool = False,
        parallel: bool = False,
    ) -> int:
        """Run tests with the specified options."""
        if watch:
            return self._run_with_watcher(app, test_path, coverage, verbose, failfast)
        else:
            return self._run_single(app, test_path, coverage, verbose, failfast, parallel)

    def _build_test_command(
        self,
        app: Optional[str] = None,
        test_path: Optional[str] = None,
        coverage: bool = False,
        verbose: bool = False,
        failfast: bool = False,
        parallel: bool = False,
    ) -> List[str]:
        """Build the pytest command with appropriate arguments."""
        cmd = ['pytest']

        # Add options
        if verbose:
            cmd.append('-v')
        if failfast:
            cmd.append('-x')
        if parallel:
            cmd.extend(['-n', 'auto'])
        if coverage:
            cmd.extend(['--cov', '--cov-report=term-missing'])

        # Add test path
        if test_path:
            cmd.append(test_path)
        elif app:
            if app in self.test_dirs:
                cmd.append(self.test_dirs[app])
            else:
                cmd.append(app)

        return cmd

    def _run_single(
        self,
        app: Optional[str],
        test_path: Optional[str],
        coverage: bool,
        verbose: bool,
        failfast: bool,
        parallel: bool,
    ) -> int:
        """Run tests once."""
        cmd = self._build_test_command(app, test_path, coverage, verbose, failfast, parallel)
        
        try:
            return subprocess.run(cmd, check=True).returncode
        except subprocess.CalledProcessError as e:
            return e.returncode

    def _run_with_watcher(
        self,
        app: Optional[str],
        test_path: Optional[str],
        coverage: bool,
        verbose: bool,
        failfast: bool,
    ) -> int:
        """Run tests with pytest-watch."""
        cmd = ['ptw']
        
        # Add pytest arguments
        test_cmd = self._build_test_command(app, test_path, coverage, verbose, failfast)
        cmd.extend(['--', *test_cmd[1:]])  # Skip 'pytest' as ptw adds it

        try:
            return subprocess.run(cmd, check=True).returncode
        except subprocess.CalledProcessError as e:
            return e.returncode
        except KeyboardInterrupt:
            return 0

    def list_tests(self, app: Optional[str] = None) -> int:
        """List available tests."""
        cmd = ['pytest', '--collect-only']
        if app:
            if app in self.test_dirs:
                cmd.append(self.test_dirs[app])
            else:
                cmd.append(app)

        try:
            return subprocess.run(cmd, check=True).returncode
        except subprocess.CalledProcessError as e:
            return e.returncode

    def run_failed(self, last_failed: bool = True) -> int:
        """Run only failed tests."""
        cmd = ['pytest']
        if last_failed:
            cmd.append('--lf')
        else:
            cmd.append('--failed')

        try:
            return subprocess.run(cmd, check=True).returncode
        except subprocess.CalledProcessError as e:
            return e.returncode

    def show_coverage(self) -> int:
        """Show the coverage report."""
        try:
            subprocess.run(['coverage', 'report'], check=True)
            subprocess.run(['coverage', 'html'], check=True)
            return 0
        except subprocess.CalledProcessError as e:
            return e.returncode

def main() -> int:
    """Parse command line arguments and run tests."""
    parser = argparse.ArgumentParser(
        description='Run tests for the Nexus Fashion Store project'
    )
    
    parser.add_argument(
        'app',
        nargs='?',
        help='App to test (core, products, cart, users) or specific test path'
    )
    
    parser.add_argument(
        '-w', '--watch',
        action='store_true',
        help='Watch for changes and re-run tests'
    )
    
    parser.add_argument(
        '-c', '--coverage',
        action='store_true',
        help='Run tests with coverage'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Run tests in verbose mode'
    )
    
    parser.add_argument(
        '-f', '--failfast',
        action='store_true',
        help='Stop on first failure'
    )
    
    parser.add_argument(
        '-p', '--parallel',
        action='store_true',
        help='Run tests in parallel'
    )
    
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List available tests'
    )
    
    parser.add_argument(
        '--failed',
        action='store_true',
        help='Run only failed tests'
    )
    
    parser.add_argument(
        '--last-failed',
        action='store_true',
        help='Run only tests that failed last time'
    )
    
    parser.add_argument(
        '--show-coverage',
        action='store_true',
        help='Show the coverage report'
    )

    args = parser.parse_args()
    runner = LocalTestRunner()

    if args.list:
        return runner.list_tests(args.app)
    elif args.failed or args.last_failed:
        return runner.run_failed(args.last_failed)
    elif args.show_coverage:
        return runner.show_coverage()
    else:
        return runner.run_tests(
            app=args.app,
            watch=args.watch,
            coverage=args.coverage,
            verbose=args.verbose,
            failfast=args.failfast,
            parallel=args.parallel,
        )

if __name__ == '__main__':
    # Set environment variables for testing
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexus.settings')
    os.environ.setdefault('DJANGO_CONFIGURATION', 'Test')
    os.environ.setdefault('PYTHONPATH', str(Path.cwd()))
    
    sys.exit(main())
