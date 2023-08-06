# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
 

setup(
    name='vcfoot',
    version='1.1.3',
    description='vcfoot by Viniette & Clarity.',
    long_description='Licensed. \
    Forbidden: Sublicense, Modifications, Distribution, Patent Grant, Use Trademark, Hold Liable.',
    author='Shoya Yasuda @ Viniette & Clarity, Inc.',
    author_email='selamatpagi1124@gmail.com',
    url='',
    license='Required: Copyright notice in any social outputs. \
    Forbidden: Sublicense, Modifications, Distribution, Patent Grant, Use Trademark, Hold Liable.',
    packages=find_packages(),
    install_requires=['numpy', 'scipy', 'opencv-python', 'Pillow', 'matplotlib', 'vcopt', 'openpyxl'],
)