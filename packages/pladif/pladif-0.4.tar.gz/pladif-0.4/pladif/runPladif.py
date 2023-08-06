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

File: runPLADIF.py
Date: Feb 2022

	simple script that run streamlit with PLADIF
"""


from inspect import getfile
import pladif
from os.path import split, join
from streamlit import cli
import sys


def runPladif():
	"""run `streamlit run mainPage.py`"""
	print("\n\n\t⚠️  Press Ctrl + C to stop PLADIF ⚠️\n\n")
	# get pladif folder
	pl, _ = split(getfile(pladif))
	# run streamlit
	sys.argv = ["streamlit", "run", join(pl, 'PLADIF.py')]
	sys.exit(cli.main())


if __name__ == '__main__':
	runPladif()
