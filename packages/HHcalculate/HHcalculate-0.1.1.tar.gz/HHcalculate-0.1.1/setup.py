#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from setuptools import find_packages, setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

required = [
    "pandas",
    "tqdm",
    "numpy",
    "biopython",
    "onnxruntime",
    "torch == 1.7.1",
]

setup(
    name="HHcalculate",
    version="0.1.1",
    author="H-H Wang",
    author_email="wanghaihua@ufl.edu",
    description="calculate number",
    license="GPL-3 License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HaihuaWang-hub/calculate",
    packages=find_packages(include=["calcualte", "calcualte.*"]),
    package_data={'': ['*.json', '*.yaml', '*.pth', '*.onnx']},

    include_package_data=True,

    classifiers=[
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'HHcalculate = HHcalculate.HHcalculate:main',
            #'ribodetector_cpu = ribodetector.detect_cpu:main',
        ]
    },
    zip_safe=True,
    install_requires=required
)
