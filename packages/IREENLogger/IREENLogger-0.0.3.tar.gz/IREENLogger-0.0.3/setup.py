import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setup(
    name="IREENLogger",
    version="0.0.3",
    author="Mostafa Asadi",
    author_email="mostafaasadi73@gmail.com",
    description="logging package for Ireen",
    long_description="logging package for Ireen",
    long_description_content_type="text/markdown",
    url="https://gitlab.com/ireen-project/ireen-data/environment/ireen-logger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=["IREENLogger"],
    package_dir={'':'IREENLogger'},
    install_requires=['redis']
)