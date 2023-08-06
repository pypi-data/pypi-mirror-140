import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quickey-python-sdk",
    version="1.0.13",
    author="quickey team",
    author_email="efrizal@analisa.io",
    description="A Login Management System for Application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/efrizal-analisa/quickey_python_sdk",
    packages=['quickey_python_sdk'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)