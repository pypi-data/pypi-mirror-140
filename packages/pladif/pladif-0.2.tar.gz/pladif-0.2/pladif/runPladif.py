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