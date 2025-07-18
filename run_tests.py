#!/usr/bin/env python
"""
Test runner script for the Nexus Fashion Store project.
Provides a CLI interface for running different types of tests with various options.
"""

import argparse
import os
import subprocess
import sys
from typing import List, Optional

# Test categories and their corresponding markers/paths
TEST_CATEGORIES = {
    'unit': {'marker': 'unit', 'path': 'tests/unit'},
    'integration': {'marker': 'integration', 'path': 'tests/integration'},
    'e2e': {'marker': 'e2e', 'path': 'tests/e2e'},
    'api': {'marker': 'api', 'path': 'tests/api'},
    'performance': {'marker': 'performance', 'path': 'tests/performance'},
}

# Test suites for specific components
TEST_SUITES = {
    'core': 'core/tests',
    'products': 'products/tests',
    'cart': 'cart/tests',
    'users': 'users/tests',
}

def run_tests(
    categories: Optional[List[str]] = None,
    suites: Optional[List[str]] = None,
    coverage: bool = True,
    verbose: bool = False,
    failfast: bool = False,
    parallel: bool = False,
    reuse_db: bool = True,
    clear_cache: bool = False,
) -> int:
    """
    Run the specified test categories and suites with the given options.
    """
    # Base pytest command
    cmd = ['pytest']

    # Add categories
    if categories:
        markers = []
        paths = []
        for category in categories:
            if category in TEST_CATEGORIES:
                markers.append(TEST_CATEGORIES[category]['marker'])
                paths.append(TEST_CATEGORIES[category]['path'])
        if markers:
            cmd.extend(['-m', ' or '.join(markers)])
        if paths:
            cmd.extend(paths)

    # Add suites
    if suites:
        suite_paths = [TEST_SUITES[suite] for suite in suites if suite in TEST_SUITES]
        if suite_paths:
            cmd.extend(suite_paths)

    # Add options
    if coverage:
        cmd.extend(['--cov=.', '--cov-report=term-missing', '--cov-report=html'])
    if verbose:
        cmd.append('-v')
    if failfast:
        cmd.append('-x')
    if parallel:
        cmd.extend(['-n', 'auto'])
    if reuse_db:
        cmd.append('--reuse-db')
    if clear_cache:
        subprocess.run(['python', 'manage.py', 'clear_cache'], check=True)

    # Set environment variables
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'nexus.settings'
    env['PYTHONPATH'] = '.'
    env['TESTING'] = 'true'

    # Run the tests
    try:
        return subprocess.run(cmd, env=env, check=True).returncode
    except subprocess.CalledProcessError as e:
        return e.returncode

def main() -> int:
    """
    Parse command line arguments and run tests accordingly.
    """
    parser = argparse.ArgumentParser(description='Run Nexus Fashion Store tests')
    
    parser.add_argument(
        '--categories',
        choices=TEST_CATEGORIES.keys(),
        nargs='+',
        help='Test categories to run'
    )
    
    parser.add_argument(
        '--suites',
        choices=TEST_SUITES.keys(),
        nargs='+',
        help='Test suites to run'
    )
    
    parser.add_argument(
        '--no-coverage',
        action='store_false',
        dest='coverage',
        help='Disable coverage reporting'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '-x', '--failfast',
        action='store_true',
        help='Stop on first failure'
    )
    
    parser.add_argument(
        '-n', '--parallel',
        action='store_true',
        help='Run tests in parallel'
    )
    
    parser.add_argument(
        '--no-reuse-db',
        action='store_false',
        dest='reuse_db',
        help='Do not reuse test database'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear cache before running tests'
    )

    args = parser.parse_args()

    # If no categories or suites specified, run all tests
    if not args.categories and not args.suites:
        args.categories = ['unit', 'integration']  # Default to unit and integration tests

    return run_tests(
        categories=args.categories,
        suites=args.suites,
        coverage=args.coverage,
        verbose=args.verbose,
        failfast=args.failfast,
        parallel=args.parallel,
        reuse_db=args.reuse_db,
        clear_cache=args.clear_cache,
    )

if __name__ == '__main__':
    sys.exit(main())
