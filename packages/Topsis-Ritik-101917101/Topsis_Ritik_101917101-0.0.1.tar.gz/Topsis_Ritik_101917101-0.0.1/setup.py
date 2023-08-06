from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
   long_description = fh.read()

setup(
    name='Topsis_Ritik_101917101',
    version='0.0.1',
    description='Topsis package Assignment-4 Ritik Raj-101917101',
    author= 'Ritik Raj',
    #url = '',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['ritik'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['Topsis_Ritik_101917101'],
    package_dir={'':'src'},
    install_requires = [
        'pandas'
    ]
)