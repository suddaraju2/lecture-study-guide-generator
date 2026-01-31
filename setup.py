"""
Setup script for Lecture Study Guide Generator.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="lecture-study-guide",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Generate comprehensive study guides from lecture materials using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lecture-study-guide-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.10",
    install_requires=[
        "python-pptx>=0.6.21",
        "pdfplumber>=0.10.0",
        "anthropic>=0.18.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anki": ["genanki>=0.13.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
        "all": [
            "openai>=1.0.0",
            "genanki>=0.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lecture-study-guide=lecture_study_guide.cli:main",
        ],
    },
)
