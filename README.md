# chemex

![chemex](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Chemex_Coffeemaker.jpg/300px-Chemex_Coffeemaker.jpg)

This project is about making public chemical hazard information more usable, by applying limited labor resources and Python.

* Transforming certain useful resources, such as hazard classification lists, into simple & uniform data formats.
* Helping to link different chemical identifiers, especially authority-controlled IDs & open structure-based IDs.

## Context

Many public sources of chemical hazard information don't have the kind of programmatic accessibility that's generally expected from [open data](http://opendefinition.org/od/2.0/en/index.html)). For the major sources of open chemical data on the web, there are helpful Python interfaces: see [PubChemPy](https://github.com/mcs07/PubChemPy), [ChemSpiPy](https://github.com/mcs07/ChemSpiPy), [CIRpy](https://github.com/mcs07/CIRpy), [BioServices](https://github.com/cokelaer/bioservices). But those resources still leave gaps in the accessibility of certain types of information, which I'm interested in.

## Organization

* `chemex` package, just a loose collection of convenient code.
* `scripts/` contains a few scripts that help transform and clean data from useful public-domain sources. See the README(s) in that directory.
  * For example, [GHS classifications](https://github.com/akokai/chemex/blob/master/scripts/README_GHS.md).
* `notebooks/` contains [notebooks](http://jupyter.org/) for explanation and/or testing.


## Requirements

* Python 3.x, or 2.7 with [future](http://python-future.org/)
* requests
* beautifulsoup4
* lxml
* pandas & numpy
* xlrd


## Fine print

Files in `data/` are from the public domain.

Everything else here is free and unencumbered software released into the public domain (see `LICENSE`).
