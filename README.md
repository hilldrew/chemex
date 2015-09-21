# chemex

![chemex](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Chemex_Coffeemaker.jpg/300px-Chemex_Coffeemaker.jpg)

This project was originally about ways of linking different kinds of identifiers (especially authority-controlled numeric IDs with open structure-based IDs) using public data, limited resources, and Python. 

It's also about transforming public chemical hazard data into more usable forms.  


## Organization

* `chemex` package.
* `scripts/` contains a few scripts that help transform and clean data from useful public-domain sources. See the README(s) in that directory.
  * [GHS classifications](https://github.com/akokai/chemex/blob/master/scripts/README_GHS.md).
  * PubChem search results.
* `notebooks/` contains [notebooks](http://jupyter.org/) for explanation and/or testing.


## Requirements

* Python 2.7 or 3.x with [future](http://python-future.org/)
* xlrd
* numpy
* pandas
* requests


## Fine print

Files in `data/` are from the public domain.

Everything else here is free and unencumbered software released into the public domain (see `LICENSE`).
