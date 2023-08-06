from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
   long_description = fh.read()

setup(
    name='topsis_deepansh_101903588',
    version='0.0.1',
    description='Topsis package by Deepansh Arora-101903588-3CO23',
    author= 'Deepansh Arora',
    #url = '',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['deepansh arora', 'tiet', 'topsis'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['topsis_deepansh_101903588'],
    package_dir={'':'src'},
    install_requires = [
        'pandas'
    ]
)