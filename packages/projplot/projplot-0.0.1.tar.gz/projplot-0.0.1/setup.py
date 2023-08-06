from setuptools import setup, find_packages
import os

VERSION = '0.0.1'
DESCRIPTION = 'A package to generate projection plots'
LONG_DESCRIPTION = 'A package that will generate projection plots to visualize optimality by altering one variable at a time.'

# Setting up
setup(
    name="projplot",
    version=VERSION,
    author="Kanika Chopra",
    author_email="<kdchopra@uwaterloo.ca",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    license='GNU General Public License v3.0',
    url='https://github.com/kanikadchopra/projplot', 
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['numpy'],
    keywords=['python', 'projection', 'plots', 'optimalty'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)