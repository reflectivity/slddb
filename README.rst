========================================
ORSO Scattering Length Density Data Base
========================================
.. image:: https://raw.githubusercontent.com/reflectivity/slddb/master/flaskr/static/orso_db.png
    :width: 15em
    :align: left

This repository contains the source code for the website https://slddb.esss.dk/slddb/ that provides
a facility to calculate neutron and x-ray scattering length densities and store associated
material parameters with proper references in a database.

The database can be accessed through a web API programatically. A python package that implements that access
is also included here.

**License**: `MIT <https://raw.githubusercontent.com/reflectivity/slddb/master/LICENSE>`_

.. image:: https://github.com/reflectivity/slddb/actions/workflows/pytest.yml/badge.svg
        :target: https://github.com/reflectivity/slddb/actions/workflows/pytest.yml
        :alt: Unit testing

.. image:: https://github.com/reflectivity/slddb/actions/workflows/codeql-analysis.yml/badge.svg
        :target: https://github.com/reflectivity/slddb/actions/workflows/codeql-analysis.yml
        :alt: CodeQL

.. image:: https://coveralls.io/repos/github/reflectivity/slddb/badge.svg?branch=master
        :target: https://coveralls.io/github/reflectivity/slddb?branch=master
        :alt: Coverage Level

Features
--------

* Databse search based on various material characteristics
* Results show selected and ORSO validated materials with unique ID to be referenced in publications
* Calculation of neutron and x-ray optical parameters from database entries and manually
  provided chemical composition and density
* Magnetic materials
* Conversion of units
* Energy dependence of x-ray with interactive selection
* Table of elements with individual scattering length and form factor values
* Assembly of protein, DNA and RNA molecules from sequence
* Interactive deuteration and hydrogen exchange calculations with D\ :sub:`2`\ O match point calculation
* User entry of new materials
* Import of CIF and FASTA file formats
* Open evaluation process for most used materials by ORSO
