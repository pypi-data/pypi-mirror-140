from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
   long_description = fh.read()

setup(
    name='Topsis_Nikhil_101917095',
    version='0.0.1',
    description='Topsis package by Nikhil 101917095 CSE4',
    author= 'Nikhil Singla',
    #url = '',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['nikhil singla', 'tiet', 'topsis'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['Topsis_Nikhil_101917095'],
    package_dir={'':'src'},
    install_requires = [
        'pandas'
    ]
)