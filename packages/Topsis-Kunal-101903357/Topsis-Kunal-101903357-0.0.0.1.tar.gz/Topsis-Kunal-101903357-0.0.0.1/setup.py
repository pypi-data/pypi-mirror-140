from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.0.1'
DESCRIPTION = 'Topsis Calculation'
setup(
    name="Topsis-Kunal-101903357",
    version=VERSION,
    author="Kunal Kashyap",
    author_email="<kunal1142000@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['topsispy', 'numpy', 'pandas'],
    keywords=['python','topsis','impacts'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)