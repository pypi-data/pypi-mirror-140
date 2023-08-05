gorpy
============

*Good Old Regex and Python*

[Read the Docs] (https://gorpy.readthedocs.io/en/latest/index.html)


Features
--------

* Written entirely in Python.
* Grep-style interface for searching text
* Pipes and union operator allow more advanced filtering of files and directory trees so that you only see the files you want
* Easily look at text inside PDFs and Word documents
* Parse XML and HTML as HTML and XML rather than just plain text
* Powerful and extensible JsonPath implementation
* Harness the power of pandas to analyze tabular documents (e.g., csv, fwf) using the same JsonPath query language
* Easily update, delete, and open files found by the tool

How to use
----------

* Install Python 3.6 or newer.
* Install

    ```sh
    # or PyPI
    pip install gorpy
    ```

* Use command-line interface to do gorp stuff:

    ```sh
    python gorp.py <query>
    ```
* or enter an interactive session:
    ```sh
    python gorp.py
    gorp> <query>
    # results
    # ...
    # more results
    gorp> <another query>
    ```
* or access gorp programmatically in a Python session (see gorp.readfiles.GorpSession)

Contributing
------------

Be sure to read the [contribution guidelines](https://github.com/molsonkiko/gorpy/blob/main/CONTRIBUTING.md). 

Other stuff
------------

TODO: add code coverage link (the below link is broken)
(https://codecov.io/github/URL-OF-PROJECT?branch=master)](https://codecov.io/OTHER-URL-OF-PROJECT)


![gorpy logo](https://github.com/molsonkiko/gorpy/blob/main/gorpy_logo_small.PNG?raw=true)

_gorpy_logo.PNG and gorpy_logo_small.PNG modified from https://commons.wikimedia.org/wiki/File:Gorp.jpg and https://www.python.org/static/community_logos/python-logo-master-v3-TM.png_