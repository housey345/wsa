"""
Setup script for WSA Terminal
This script can be used to create an executable using PyInstaller
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wsa-terminal",
    version="1.0.0",
    author="WSA Team",
    description="WSA Terminal - Windows Subsystem for Amiga",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    entry_points={
        'console_scripts': [
            'wsa=wsa:main',
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)