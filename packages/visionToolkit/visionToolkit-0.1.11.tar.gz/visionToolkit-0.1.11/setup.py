# -*- coding: utf-8 -*-

from setuptools import find_packages, setup


setup(
    name='visionToolkit',
    packages=find_packages(),
    version='0.1.11',
    description='Gaze Analysis Library',
    author='Laborde Perochon Roques',
    license='ENS_Paris_Saclay',
    install_requires=['hilbertcurve',
                      'scipy',
                      'scikit-learn'],
)