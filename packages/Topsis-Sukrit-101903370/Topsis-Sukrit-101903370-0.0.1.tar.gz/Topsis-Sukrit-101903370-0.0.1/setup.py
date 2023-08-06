from setuptools import setup, find_packages
import codecs
import os



VERSION = '0.0.1'
DESCRIPTION = 'Topsis rank genrator'
LONG_DESCRIPTION = 'Topsis is a comparator model which allows user to select the best option amongst all the options'

# Setting up
setup(
    name="Topsis-Sukrit-101903370",
    version=VERSION,
    author="Sukrit Bansal",
    author_email="<sukritbansal01@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[ 'pandas', 'numpy'],
    keywords=['python','numpy','rank','score',],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
