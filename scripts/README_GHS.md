# ghs.py

These are Python scripts for extracting Globally Harmonised System (GHS) hazard classification information for chemicals from various international government documents, and transforming it into uniformly structured data formats.

For information on the Globally Harmonised System of Classification and Labelling of Chemicals, see [the UNECE's GHS website](http://www.unece.org/trans/danger/publi/ghs/ghs_welcome_e.html).


The data sources are the official published classification documents from the following national GHS implementations. 


## Japan: GHS Classifications

> N.B. This script has been updated and now works differently.

* All available classification results can be downloaded from the [NITE GHS website](http://www.safe.nite.go.jp/english/ghs/ghs_download.html) using the script `ghs_jp_download.py`.
* Input data files are in `/data/ghs/jp/`, output is in `/results/ghs/jp/`.

### How the data source is organized

Several batches of classifications are distributed in series of Excel workbooks. There are batches of 'new' classifications, and batches of revisions to earlier ones. Each workbook contains many sheets, with each sheet describing the classification results for a single chemical in an (almost) identical layout. Chemicals are identified by an index ID (inconsistent/incomplete), 
zero or more CASRNs, and chemical name. 

For each hazard class, the spreadsheets tabulate the following results of chemical evaluations: 

- Classification
- Symbol (named)
- Signal word
- Hazard statement (unfortunately without H-statement codes)
- Rationale for classification

This script *does not* take account of the PDF files provided on the NITE website which describe a limited number of individual errata/corrigenda. However, it seems that these errors have already been corrected in the XLS dataset which the script retrieves.

### What the program does

Compiles the cumulative results of all chemical classifications and revisions. Produces two kinds of output:

- A single JSON object organized by chemical.
- A series of Excel spreadsheets organized by hazard class -- one XLSX file per hazard class, one chemical per row.

**Note on identifiers:** If there are multiple CASRNs per chemical, then this script creates an identical entry for each of them, which also specifies a list of all the CASRNs associated with it. This is a compromise, and a decision that errs on the side of more aliasing. Such is life with CASRNs.

### How to run it

* Download the data: `python ghs_jp_download.py`
* Run the script: `python ghs.py jp`


## Republic of Korea: GHS Classifications

> N.B. This section may be out of date.

* The amended list of GHS classification and labelling for toxic chemicals (2011) by the National Institute of Environmental Research
* [NIER GHS Main page](http://ncis.nier.go.kr/ghs/)
* Downloaded from [this page](http://ncis.nier.go.kr/ghs/search/searchlist_view.jsp?seq=17)
* Input data files are in `/data/ghs/kr/`, output is in `/results/ghs/kr/`.

**What the program does:** Reads the spreadsheet of Korean GHS classifications and produces `GHS-kr/output/GHS-kr.csv`, containing a table of substance names, CASRN, combined hazard class/category/H-statements (in English), and M-factors. It further produces a text file `GHS-kr/output/sublists.txt` containing a list of all unique combined hazard class/category/H-statement fields that appear in the dataset.

**How the data source is organized:** The document is in 한국어, with only substance names in English. It is straightforwardly structured and includes numeric GHS chapter references for hazard classes, and H-statement codes. I was able to convincingly translate the key elements of the document using Google Translate (some of my notes are in `GHS-kr/GHS-kr-trans-attempt.ods`, LibreOffice spreadsheet). 

In the original spreadsheet, each line describes one substance with one hazard classification. Columns E-F are the hazard class and category, respectively (e.g. the first one is Oxidizing solids (2.14), Category 3). Columns G-J are for labelling, respectively: symbol (coded), signal word, and hazard statement (coded), and M-factor. The program takes into account the multi-row merged cells which span classifications for the same CASRN (to avoid having many empty CASRN fields).

Using the hazard class names allows (via Google Translate) distinguishing the following hazards that have the same GHS chapter number:
* 급성 독성-경구 (3.1) = Acute toxicity - oral
* 급성 독성-경피 (3.1) = Acute toxicity - dermal
* 급성 독성-흡입 (3.1) = Acute toxicity - inhalation
* 피부 과민성 (3.4) = Skin sensitization
* 호흡기 과민성 (3.4) = Respiratory sensitization
* 수생환경유해성-급성 (4.1) = Hazardous to the aquatic environment - acute
* 수생환경유해성-만성 (4.1) = Hazardous to the aquatic environment - chronic


## Aotearoa New Zealand: HSNO Chemical Classifications

> N.B. This section may be out of date.

* Classifications from the Environmental Protection Authority's [Chemical Classification and Information Database (CCID)](http://www.epa.govt.nz/search-databases/Pages/HSNO-CCID.aspx)
* Data source: File `CCID Key Studies (2014-05-26).xls`, obtained from NZ EPA via Healthy Building Network.
* The correlation between HSNO classifications and GHS Rev. 3 classifications is described in [a document](http://www.epa.govt.nz/Publications/hsnogen-ghs-nz-hazard.pdf) (PDF), which is also included in this repo.
* Input data files are in `/data/ghs/nz/`, output is in `/results/ghs/nz/`.

**What the program does:** Reads data exported from the HSNO CCID, and produces CSV files containing chemical IDs, names, classifications, and key studies (basis for classification). The program adds GHS translations to each HSNO classification, according to the document cited above. 

The program filters the dataset in order to separate information that might be considered redundant from a broad chemical hazard assessment perspective: classifications of solutions of other substances. The filtering algorithm looks at substances which share the same CASRN but have different names, and seems to work reasonably well for this dataset. Three output files are produced: The main file `GHS-nz.csv` contains classifications of pure substances. 'Redundant' substances are written to `exclude.csv`, and are almost all solutions whose classifications are a subset of the pure substance's classifications. Solutions that appear to have unique classifications (not a subset of the pure substance's classifications) are written to `variants.csv`. In the latter two output files, CASRN values for each different substance are preceded by "_v" + a sequential number, to help with identifier wrangling.

Finally, the program produces `sublists.csv`, a table of all unique classification codes that appear in the dataset, along with the full text of their HSNO and corresponding GHS classifications.

**How the data source is organized:** The spreadsheet is a data export from the HSNO CCID. It contains chemical names, CASRN, classification codes and text, and summaries of the key toxicological studies or data that inform each classification. There is one classification per row in the spreadsheet (23168 classifications). Substances are identified non-uniquely by CASRN, and uniquely by name – that is, multiple variants share the same CASRN.

