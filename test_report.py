#!/usr/bin/env python
"""
Test report generator for the Nexus Fashion Store project.
Generates detailed HTML and JSON reports from test results.
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest
from jinja2 import Environment, FileSystemLoader

# Constants
REPORT_DIR = Path("test_reports")
TEMPLATE_DIR = Path("templates/reports")
COVERAGE_DIR = Path("htmlcov")


class TestReportGenerator:
    def __init__(self) -> None:
        """Initialize the test report generator."""
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_dir = REPORT_DIR / self.timestamp
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=True
        )

    def run_tests(self) -> Tuple[int, Dict[str, Any]]:
        """
        Run the test suite and collect results.
        Returns tuple of (exit_code, test_results).
        """
        # Create pytest arguments
        pytest_args = [
            "--verbose",
            "--cov=.",
            "--cov-report=html",
            "--cov-report=json",
            f"--junitxml={self.report_dir}/junit.xml",
            "--html={self.report_dir}/report.html",
            "--self-contained-html",
        ]

        # Run tests and collect results
        test_results: Dict[str, Any] = {}
        exit_code = pytest.main(pytest_args)
        
        # Move coverage reports
        if (Path("coverage.json").exists()):
            with open("coverage.json") as f:
                test_results["coverage"] = json.load(f)
            os.rename("coverage.json", self.report_dir / "coverage.json")

        if COVERAGE_DIR.exists():
            os.rename(COVERAGE_DIR, self.report_dir / "coverage")

        return exit_code, test_results

    def collect_metadata(self) -> Dict[str, Any]:
        """Collect metadata about the test environment."""
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], 
            universal_newlines=True
        ).strip()

        git_branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            universal_newlines=True
        ).strip()

        return {
            "timestamp": self.timestamp,
            "git_hash": git_hash,
            "git_branch": git_branch,
            "python_version": sys.version,
            "platform": sys.platform,
        }

    def collect_test_stats(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Collect statistics about test results."""
        coverage_data = test_results.get("coverage", {})
        totals = coverage_data.get("totals", {})

        return {
            "coverage_percentage": totals.get("percent_covered", 0),
            "covered_lines": totals.get("covered_lines", 0),
            "total_lines": totals.get("num_statements", 0),
            "missing_lines": totals.get("missing_lines", 0),
        }

    def generate_html_report(
        self,
        metadata: Dict[str, Any],
        test_stats: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> None:
        """Generate HTML report from test results."""
        template = self.jinja_env.get_template("test_report.html")
        
        report_data = {
            "metadata": metadata,
            "stats": test_stats,
            "results": test_results,
        }
        
        html_output = template.render(**report_data)
        
        with open(self.report_dir / "index.html", "w") as f:
            f.write(html_output)

    def generate_json_report(
        self,
        metadata: Dict[str, Any],
        test_stats: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> None:
        """Generate JSON report from test results."""
        report_data = {
            "metadata": metadata,
            "stats": test_stats,
            "results": test_results,
        }
        
        with open(self.report_dir / "report.json", "w") as f:
            json.dump(report_data, f, indent=2)

    def generate_badge(self, coverage_percentage: float) -> None:
        """Generate a coverage badge."""
        if coverage_percentage >= 90:
            color = "brightgreen"
        elif coverage_percentage >= 80:
            color = "green"
        elif coverage_percentage >= 70:
            color = "yellowgreen"
        elif coverage_percentage >= 60:
            color = "yellow"
        else:
            color = "red"

        badge_data = {
            "schemaVersion": 1,
            "label": "coverage",
            "message": f"{coverage_percentage:.1f}%",
            "color": color
        }

        with open(self.report_dir / "coverage-badge.json", "w") as f:
            json.dump(badge_data, f)

    def run(self) -> int:
        """
        Run the complete test report generation process.
        Returns the exit code from the test run.
        """
        print("Running tests and generating reports...")
        
        # Run tests
        exit_code, test_results = self.run_tests()
        
        # Collect data
        metadata = self.collect_metadata()
        test_stats = self.collect_test_stats(test_results)
        
        # Generate reports
        self.generate_html_report(metadata, test_stats, test_results)
        self.generate_json_report(metadata, test_stats, test_results)
        self.generate_badge(test_stats["coverage_percentage"])
        
        # Print summary
        print("\nTest Report Summary:")
        print(f"Coverage: {test_stats['coverage_percentage']:.1f}%")
        print(f"Total Lines: {test_stats['total_lines']}")
        print(f"Covered Lines: {test_stats['covered_lines']}")
        print(f"Missing Lines: {test_stats['missing_lines']}")
        print(f"\nReports generated in: {self.report_dir}")
        
        return exit_code


def create_report_template() -> None:
    """Create the HTML template for test reports if it doesn't exist."""
    template_dir = TEMPLATE_DIR
    template_dir.mkdir(parents=True, exist_ok=True)
    
    template_path = template_dir / "test_report.html"
    if not template_path.exists():
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {{ metadata.timestamp }}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8">Test Report</h1>
        
        <!-- Metadata -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Metadata</h2>
            <dl class="grid grid-cols-2 gap-4">
                <dt class="font-medium">Timestamp:</dt>
                <dd>{{ metadata.timestamp }}</dd>
                
                <dt class="font-medium">Git Hash:</dt>
                <dd>{{ metadata.git_hash }}</dd>
                
                <dt class="font-medium">Git Branch:</dt>
                <dd>{{ metadata.git_branch }}</dd>
                
                <dt class="font-medium">Python Version:</dt>
                <dd>{{ metadata.python_version }}</dd>
                
                <dt class="font-medium">Platform:</dt>
                <dd>{{ metadata.platform }}</dd>
            </dl>
        </div>
        
        <!-- Statistics -->
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Test Statistics</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="p-4 bg-blue-100 rounded-lg">
                    <div class="text-2xl font-bold text-blue-700">{{ "%.1f"|format(stats.coverage_percentage) }}%</div>
                    <div class="text-sm text-blue-600">Coverage</div>
                </div>
                
                <div class="p-4 bg-green-100 rounded-lg">
                    <div class="text-2xl font-bold text-green-700">{{ stats.covered_lines }}</div>
                    <div class="text-sm text-green-600">Covered Lines</div>
                </div>
                
                <div class="p-4 bg-yellow-100 rounded-lg">
                    <div class="text-2xl font-bold text-yellow-700">{{ stats.total_lines }}</div>
                    <div class="text-sm text-yellow-600">Total Lines</div>
                </div>
                
                <div class="p-4 bg-red-100 rounded-lg">
                    <div class="text-2xl font-bold text-red-700">{{ stats.missing_lines }}</div>
                    <div class="text-sm text-red-600">Missing Lines</div>
                </div>
            </div>
        </div>
        
        <!-- Coverage Details -->
        {% if results.coverage %}
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold mb-4">Coverage Details</h2>
            <div class="overflow-x-auto">
                <table class="min-w-full table-auto">
                    <thead>
                        <tr class="bg-gray-100">
                            <th class="px-4 py-2 text-left">File</th>
                            <th class="px-4 py-2 text-right">Coverage</th>
                            <th class="px-4 py-2 text-right">Lines</th>
                            <th class="px-4 py-2 text-right">Missing</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for file, data in results.coverage.files.items() %}
                        <tr class="border-t">
                            <td class="px-4 py-2">{{ file }}</td>
                            <td class="px-4 py-2 text-right">{{ "%.1f"|format(data.summary.percent_covered) }}%</td>
                            <td class="px-4 py-2 text-right">{{ data.summary.num_statements }}</td>
                            <td class="px-4 py-2 text-right">{{ data.summary.missing_lines|length }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
        """
        
        with open(template_path, "w") as f:
            f.write(template_content)


def main() -> int:
    """Main entry point for the test report generator."""
    try:
        create_report_template()
        generator = TestReportGenerator()
        return generator.run()
    except Exception as e:
        print(f"Error generating test report: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
