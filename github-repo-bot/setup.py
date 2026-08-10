#!/usr/bin/env python3
"""
Setup script for GitHub Repository Enhancement Bot
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="github-repo-enhancement-bot",
    version="1.0.0",
    author="Professional Development Team",
    author_email="dev@codepulse.dev",
    description="A comprehensive GitHub repository automation and enhancement tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/github-repo-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "github-repo-bot=bot:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)