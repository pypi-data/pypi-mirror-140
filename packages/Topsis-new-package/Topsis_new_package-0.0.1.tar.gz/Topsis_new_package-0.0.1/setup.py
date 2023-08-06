from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Topsis:-a package to pick best model'

# Setting up
setup(
    name="Topsis_new_package",
    version=VERSION,
    author="Sourav Khanna",
    author_email="<souravkhanna227@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['opencv-python', 'numpy','pandas'],
    keywords=['python', 'model', 'best', 'test', 'topsis'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)