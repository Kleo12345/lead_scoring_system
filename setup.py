from setuptools import setup, find_packages

setup(
    name="gym-lead-scorer",
    version="1.0.0",
    description="AI-powered lead scoring system for gym marketing agencies",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        line.strip() 
        for line in open('requirements.txt').readlines() 
        if not line.startswith('#')
    ],
    entry_points={
        'console_scripts': [
            'score-leads=src.main:main',
        ],
    },
    python_requires='>=3.8',
)
