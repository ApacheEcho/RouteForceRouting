"""
Setup configuration for RouteForce Routing
"""

from setuptools import setup, find_packages
import os

# Read version from VERSION file
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return "0.1.0"

# Read README for long description
def get_long_description():
    readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_file):
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def get_requirements():
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle version pinning and comments
                    req = line.split('#')[0].strip()
                    if req:
                        requirements.append(req)
            return requirements
    return []

setup(
    name="routeforce-routing",
    version=get_version(),
    author="ApacheEcho",
    author_email="",
    description="A route optimization engine for field execution teams",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/ApacheEcho/RouteForceRouting",
    project_urls={
        "Bug Tracker": "https://github.com/ApacheEcho/RouteForceRouting/issues",
        "Documentation": "https://github.com/ApacheEcho/RouteForceRouting/blob/main/README.md",
        "Source Code": "https://github.com/ApacheEcho/RouteForceRouting",
        "Changelog": "https://github.com/ApacheEcho/RouteForceRouting/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "app": [
            "static/**/*",
            "templates/**/*",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
    ],
    python_requires=">=3.11",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.0.0",
            "black>=25.0.0",
            "flake8>=7.0.0",
            "mypy>=1.0.0",
        ],
        "deployment": [
            "gunicorn>=23.0.0",
            "eventlet>=0.37.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "routeforce=app:create_app",
        ],
    },
    keywords="routing optimization logistics fleet management",
    zip_safe=False,
)