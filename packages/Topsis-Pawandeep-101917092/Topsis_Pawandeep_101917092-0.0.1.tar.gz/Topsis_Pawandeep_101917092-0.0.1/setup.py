from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
   long_description = fh.read()

setup(
    name='Topsis_Pawandeep_101917092',
    version='0.0.1',
    description='Topsis package for Predictive Analysis Assignement made by Pawandeep_101917092',
    author= 'Pawandeep Singh',
    #url = '',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['pawandeep'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['Topsis_Pawandeep_101917092'],
    package_dir={'':'src'},
    install_requires = [
        'pandas'
    ]
)