# chemex

![chemex](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Chemex_Coffeemaker.jpg/300px-Chemex_Coffeemaker.jpg)

This project is about making public chemical hazard information more usable, by applying limited labor resources and Python.

* Transforming certain useful resources, such as hazard classification lists, into simple & uniform data formats.
* Helping to link different chemical identifiers, especially authority-controlled IDs & open structure-based IDs.


## Organization

* `chemex` package, just a loose collection of convenient functions.
* `scripts/` contains a few scripts that help transform and clean data from useful public-domain sources. See the README(s) in that directory.
  * [GHS classifications](https://github.com/akokai/chemex/blob/master/scripts/README_GHS.md).
  * PubChem search results.
* `notebooks/` contains [notebooks](http://jupyter.org/) for explanation and/or testing.


## Requirements

* Python 3.x, or 2.7 with [future](http://python-future.org/)
* lxml
* numpy
* pandas
* requests
* xlrd


## Fine print

Files in `data/` are from the public domain.

Everything else here is free and unencumbered software released into the public domain (see `LICENSE`).


## See also

There are some solid Python interfaces for accessing major open chemical data services on the web.

* [PubChemPy](https://github.com/mcs07/PubChemPy)
* [ChemSpiPy](https://github.com/mcs07/ChemSpiPy)
* [CIRpy](https://github.com/mcs07/CIRpy)
* [BioServices](https://github.com/cokelaer/bioservices)