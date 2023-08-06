========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions| |travis| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/Time_Frequency_Analysis/badge/?style=flat
    :target: https://Time_Frequency_Analysis.readthedocs.io/
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/nnanos/Time_Frequency_Analysis.svg?branch=main
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/github/nnanos/Time_Frequency_Analysis

.. |github-actions| image:: https://github.com/nnanos/Time_Frequency_Analysis/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/nnanos/Time_Frequency_Analysis/actions

.. |requires| image:: https://requires.io/github/nnanos/Time_Frequency_Analysis/requirements.svg?branch=main
    :alt: Requirements Status
    :target: https://requires.io/github/nnanos/Time_Frequency_Analysis/requirements/?branch=main

.. |codecov| image:: https://codecov.io/gh/nnanos/Time_Frequency_Analysis/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://codecov.io/github/nnanos/Time_Frequency_Analysis

.. |version| image:: https://img.shields.io/pypi/v/Time-Frequency-Analysis.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/Time-Frequency-Analysis

.. |wheel| image:: https://img.shields.io/pypi/wheel/Time-Frequency-Analysis.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/Time-Frequency-Analysis

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/Time-Frequency-Analysis.svg
    :alt: Supported versions
    :target: https://pypi.org/project/Time-Frequency-Analysis

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/Time-Frequency-Analysis.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/Time-Frequency-Analysis

.. |commits-since| image:: https://img.shields.io/github/commits-since/nnanos/Time_Frequency_Analysis/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/nnanos/Time_Frequency_Analysis/compare/v0.0.0...main



.. end-badges

Time frequency transforms under the mathematical framework of frames

* Free software: MIT license

Installation
============

::

    pip install Time-Frequency-Analysis

You can also install the in-development version with::

    pip install https://github.com/nnanos/Time_Frequency_Analysis/archive/main.zip



Usage
=============
::
    afdgdfsdg



Documentation
=============


https://Time_Frequency_Analysis.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
