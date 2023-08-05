
from setuptools import setup

with open("/Users/gsp/Desktop/Data science/Udacity data science /Lessons/Python code/Object oriented programming/mplot/README.md", "r") as fh:
	long_description = fh.read()

setup(
	name = 'mplot_plots',
	version = '1.1',
	description = 'Diagnostic plots for linear model',
	py_modules = ["mplot"],
	package_dir = {'': 'mplot_plots'},
	classifiers = [
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.6",
			"Programming Language :: Python :: 3.7", 
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent"
		],
	long_description = long_description,
	long_description_content_type = "text/markdown",
	author = 'Geofrey Wanyama',
	url = 'https://gitlab.com/gspwanyama97/mplot_plot',
	author_email = 'wanyamag17@gmail.com',
	zip_safe = False,
	)

