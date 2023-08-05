""""This file is part of PLADIF.

	MIT License

	Copyright (c) 2022 - Thibault Hilaire

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.


PLADIF is a simple tool that plots attrakdiff graphs from CSV files (like those from Usabilla).
It is written by Thibault Hilaire

File: setup.py
Date: Feb 2022

	setup.py file to install PLADIF
"""


from setuptools import setup


def readme():
    """include the readme"""
    with open('README.md') as f:
        return f.read()


setup(name='pladif',
      version='0.2',
      description="PLADIF is a simple tool that plot attrakdiff graphs from CSV files (like those from Usabilla)",
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Intended Audience :: Other Audience'
      ],
      keywords='CSV, attrakdiff, Usabilla',
      url='https://github.com/thilaire/PLADIF',
      author='Thibault Hilaire',
      author_email='thibault@docmatic.fr',
      license='MIT',
      packages=['pladif'],
      install_requires=['matplotlib', 'pandas', 'streamlit', 'scipy'],
      entry_points={'console_scripts': ['runPLADIF=pladif.runPladif:runPladif']},
      include_package_data=True,
      zip_safe=False
)
