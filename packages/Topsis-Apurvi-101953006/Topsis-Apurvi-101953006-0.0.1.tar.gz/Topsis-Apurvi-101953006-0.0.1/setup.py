from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Multi-Criteria Decision Making'
LONG_DESCRIPTION = 'A package to rank the models on the basis of TOPSIS method'

# Setting up
setup(
    name="Topsis-Apurvi-101953006",
    version=VERSION,
    author="Apurvi",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    license="MIT",
    packages=["Topsis_Apurvi_101953006"],
    install_requires='pandas',
    include_package_data=True,
    keywords=['python', 'best model', 'Topsis', 'multi-criteria decision making', 'assignment'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "topsis=Topsis_Apurvi_101953006.101953006:main",
        ]
    },
)