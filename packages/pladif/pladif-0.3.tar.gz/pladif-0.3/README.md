# PLADIF: Plots Attrakdiff graphs from CSV files

[Attrakdiff](http://www.attrakdiff.de/index-en.html) is a method to evaluate UX aspects like attractivity, usability, desirability, etc.

[Usabilla](https://usabilla.com/) is a software that is able to get feedback from online customers.

**PLADIF** is a simple tool that plots attrakdiff plots from CSV file (like those prroduced by Usabilla). It is based on Python, matplotlib, pandas and streamlit. It's a web-app that can be installed locally or hosted in a web server.

**A live demo can be found [here](https://share.streamlit.io/thilaire/pladif/main/pladif/PLADIF.py)**

The web-app takes Usabilla's CSV files as input, and produces attrakdiff graphes as output.
![screenshot](doc/screenshot.png)

It produces the three diagrams of the Attrakdiff method:
#### Diagram of average values
![diagram of average values](doc/plotAverageValues.jpg)
#### Description of word-pairs
![Description of word-pairs](doc/plotWordPair.jpg)
#### The portfolio presentation
![Portfolio presentation](doc/plotAttrakdiff.jpg)



## Installation
PLADIF is a web-app done using Python, [matplotlib](https://matplotlib.org/) (for the plots), [pandas](https://pandas.pydata.org/) (for the data manipulation) and [streamlit](https://streamlit.io/) (for the web-app). These libraries are way overkill for a such simple tool, but it made my development much easier 😀 !
### On Mac or Linux
To install it, you need to have a machine with Python3 installed. You then just need to install the `pladif` library, with
```
pip3 install pladif
```

and that's it ! (ok, it will install a lot of things, specially if you don't use python for anything else).
The right way to do it, is of course to do it in a virtuel environment.
On a fresh Mac, the system will probably ask to install some developper tools first (do it).

### On Windows machine
You probably need to install it using [Conda](https://docs.conda.io/en/latest/), and then install the `pladif` package.

## run PLADIF
To run PLADIF, just launch the `runPladif` script
```
runPladif
```
(if `runPladif` doesn't work, it means the package `pladif` is installed, but not added in your path)

On a first run, streamlit will ask for an email, juste press Return (never give your email address to strangers 😉). You then have the following message
```


	⚠️  Press Ctrl + C to stop PLADIF ⚠️



  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.18:8501

  For better performance, install the Watchdog module:

  $ xcode-select --install
  $ pip install watchdog
```
and it means that it works ! It should also open a tab on your web browser, with PLADIF open. 
Don't forget to close PLADIF (the server) with Ctrl+C when you don't use it (close the browser tab is not enough)

## Use it
It's quite simple. Just drag'n drop your CSV files (from Usabilla) on the left panel, and that's it.
You can change the lang (English or French for the moment, Deutsch should arrive soon), or adjust the interval confidence level.
You can download each image (with the download button below each image).

## TODO
- add Deutsch support
- support other CSV file (for the moment, only Usabilla's one are supported, ie CSV with UTF-16 encoding and tab as delimiter)
- integrate all the feedback you may send (just open an issue on GitHub)
- add a CSV (or excel) report, with all the data
- add a pdf report


## I hope it will be useful
If PLADIF is useful, buy me a beer 🍺 !

Disclaimer: I am not affiliate to Usabilla nor Attrakdiff. This is a simple python tool for that. It uses [matplotlib](https://matplotlib.org/) for the graphs and [pandas](https://pandas.pydata.org/) for manipulatin the data (I am not a pandas expert, and probably some code that be done more efficiently with the adequate pandas methods). [Streamlit](https://streamlit.io/) is used for the web app. It is maybe not the *best* choice for PLADIF, but I wanted to try it!
