# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='sagar-malaviya-greet',
    version='2.0.0',
    description='A sample Python project to greet',
    author='Sagar Malaviya',
    author_email='sagar.malaviya@crestdatasys.com',
    classifiers=[
        "Programming Language :: Python :: 3.10",
    ],
    keywords='greet, python, development',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    )
