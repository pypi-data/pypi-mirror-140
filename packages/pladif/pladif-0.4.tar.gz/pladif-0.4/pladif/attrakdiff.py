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

File: attrakdiff.py
Date: Feb 2022

	Plot functions
"""


from typing import Dict, List
from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from scipy import stats
from io import BytesIO
import pandas as pd


from pladif.naming import categories, titles, order_long, order_short, pairs
from pladif.naming import i18n_dim, i18n_average, QPQH, plt_avrg, plt_pair, plt_attr


def interval(data, alpha):
	"""Apply Student's t-distribution to get the confidence interval around the mean
	according to alpha (alpha=0.05 for a 95% confidence interval)
	returns the mean (center of the interval) and the interval (center of the interval)
	"""
	# We use Student's t-distribution to compute the confidence interval
	# see https://en.wikipedia.org/wiki/Student%27s_t-distribution
	mean = data.mean()
	inter = stats.t.interval(alpha, len(data) - 1, loc=mean, scale=stats.sem(data))
	return mean, inter[0], inter[1]





def loadCSV(file: [BytesIO, str]):
	"""Load the data from an (already open) excel file
	The data is normalize in [-3,3]
	Return a dataframe"""
	# read the excel file into a dataframe
	Tab = read_csv(file, index_col=0, encoding="UTF-16", delimiter='\t')    # encoding=None, encoding_errors="replace"
	# drop all the columns after the URL column
	try:
		url_index = Tab.columns.get_loc("URL")
	except KeyError:
		raise ValueError("The csv file is not a valid Usabilla one (does not contain a 'URL' column) !")
	Tab.drop(columns=Tab.columns[url_index:], inplace=True)
	# check the size and rename the columns
	if len(Tab.columns) not in [len(order_short), len(order_long)]:
		raise ValueError("The csv file is not a valid Usabilla one (doesn not have %d or %d useful columns)"
		                 % (len(order_short), len(order_long)))
	Tab.columns = order_short if len(Tab.columns) == len(order_short) else order_long
	# normalize data in [-3,3]
	for col, serie in Tab.items():
		if '*' in col:
			Tab[col] = 4-Tab[col]   # reverse from 3 to -3
		else:
			Tab[col] = Tab[col]-4   # from -3 to 3
	# remove the '*' and sort the columns (same order as the ordered dictionary `pairs`
	Tab.columns = [(st[:-1] if '*' in st else st) for st in Tab.columns]
	d = {k: v for v, k in enumerate(pairs)}
	Tab = Tab.reindex(columns=sorted(Tab.columns, key=d.get))
	return Tab


def cat2dict(data: DataFrame) -> Dict[str, List[str]]:
	"""Returns the dictionary of the categories used
	Ex: {'QP': ['QP1','QP2'], 'ATT': ['ATT1']} """
	# groups categories
	return {name: [col for col in data.columns if name in col] for name in categories}


def plotAverageValues(ax: plt.Axes, datas: Dict[str, DataFrame], alpha: float, lang: str):
	"""Plot the diagrame of average values
	and returns the associated dataFrame"""
	cat = cat2dict(datas[next(iter(datas))])
	data = DataFrame.from_dict(
		{name: {name: list(interval(dF[cat].stack(), alpha)) for name, cat in cat.items()} for name, dF in datas.items()}
	)
	data = data.reindex(cat.keys())

	for name, d in data.items():
		T = DataFrame.from_dict({c: v for c, v in d.items()})
		plt.plot(T.loc[0], marker='o')
		plt.fill_between(range(len(T.columns)), T.loc[1], T.loc[2], alpha=0.1)

	plt.xlabel(i18n_dim[lang])
	plt.ylabel(i18n_average[lang])
	plt.ylim(-3, 3)
	plt.setp(ax.get_xticklabels(), y=0.5)
	plt.grid()
	plt.title(plt_avrg[lang])
	return data.applymap(lambda x: "%.2f: [%.2f;%.2f]" % tuple(x)) if alpha else data.applymap(lambda x: x[0])



def plotWordPair(ax: plt.Axes, datas: Dict[str, DataFrame], alpha: float, lang: str):
	"""Draw the diagram of word-pairs
	and return the associated dataframe"""
	columns = datas[next(iter(datas))].columns
	plt.plot([0, 0], [len(columns) + 0.5, 0.5], 'k')
	# plot each line
	dd = DataFrame.from_dict({name: {col: interval(dF[col], alpha) for col in columns} for name, dF in datas.items()})
	for name, data in dd.items():
		T = DataFrame.from_dict({c: v for c, v in data.items()})
		plt.plot(T.loc[0], range(len(T.columns), 0, -1), 's-', label=name)
		plt.fill_betweenx(range(len(T.columns), 0, -1), T.loc[1], T.loc[2], alpha=0.1)
	plt.legend()
	# add rectangle for each category
	y = 1
	xpos = {'en': -5.3, 'fr': -5.8, 'de': -4}        # TODO: computes it automatically (get minimum position of all labels)
	length = {'en': 11, 'fr': 11.3, 'de': 8}
	for cat, color in zip(categories, ['skyblue', 'orchid', 'pink', 'palegreen']):
		size = len([x for x in columns if cat in x])
		ax.add_patch(FancyBboxPatch((xpos[lang], y), length[lang], size-1, fill=True, alpha=0.2, clip_on=False, color=color))
		plt.text(xpos[lang]-0.2, y+size/2-0.5, cat, clip_on=False, rotation='vertical', verticalalignment='center')
		y += size

	# set axes, and pair words as left/right labels
	labelsL = [pairs[col][lang][0] for col in datas[next(iter(datas))].T.index] + [""]
	labelsR = [pairs[col][lang][1] for col in datas[next(iter(datas))].T.index] + [""]
	labelsL.reverse()
	labelsR.reverse()
	ax.set_yticks(range(len(labelsL)), labels=labelsL)
	ax.set_ylim(len(columns)+0.5, 0.5)
	axR = ax.twinx()
	axR.set_yticks(range(len(labelsR)), labels=labelsR)
	axR.set_ylim(len(columns)+0.5, 0.5)
	plt.xlim([-3, 3])

	ax.grid(visible=True)
	ax.set_box_aspect(1.25)
	plt.title(plt_pair[lang])

	return dd.applymap(lambda x: "%.2f: [%.2f;%.2f]" % tuple(x)) if alpha else dd.applymap(lambda x: x[0])



def plotAttrakdiff(ax: plt.Axes, datas: Dict[str, DataFrame], alpha: float, lang: str):
	"""Plot the Attrakdiff portfolio
	and return the associated dataframe"""
	plt.xlim([-3, 3])
	plt.ylim([-3, 3])
	ax.xaxis.set_ticks([-3, -1, 1, 3])
	ax.yaxis.set_ticks([-3, -1, 1, 3])
	plt.grid()
	for i in [-2, 0, 2]:
		for j in [-2, 0, 2]:
			if (i, j) in QPQH:
				plt.text(i, j, QPQH[i, j][lang], alpha=0.5, ha='center', va='center', zorder=-5)
	plt.xlabel(titles["QP"][lang])
	plt.ylabel(titles["QH"][lang])

	cat = cat2dict(datas[next(iter(datas))])
	attr = {}
	for name, data in datas.items():
		# get QH and QP
		QH = data[cat["QHI"]+cat["QHS"]]
		QP = data[cat["QP"]]
		x, ixm, ixp = interval(QP.stack(), alpha)
		y, iym, iyp = interval(QH.stack(), alpha)
		# plot point
		p = plt.plot(x, y, 'o', label=name)
		# plot interval
		if alpha:
			ax.add_patch(Rectangle((ixm, iym), ixp-ixm, iyp-iym, fill=True, alpha=0.2, color=p[0].get_color()))

		if alpha:
			attr[name] = {"QP": "%.2f: [%.2f;%.2f]" % (x, ixm, ixp), "QH": "%.2f: [%.2f;%.2f]" % (y, iym, iyp)}
		else:
			attr[name] = {"QP": x, "QH": y}

	plt.legend()
	plt.title(plt_attr[lang])
	return pd.DataFrame.from_dict(attr)


# ONLY USED FOR INTERN TESTING
if __name__ == '__main__':
	X = loadCSV("../resources/exp2.csv")
	# fig, ax = plt.subplots()
	# plotWordPair({'toto': X})
	f, a = plt.subplots()
	plotAverageValues(a, {'toto': X}, 0.95, 'en')
	plt.show()
