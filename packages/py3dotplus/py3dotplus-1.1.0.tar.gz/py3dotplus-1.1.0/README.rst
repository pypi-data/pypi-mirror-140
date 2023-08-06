========================================================
Py3DotPlus - Python interface to Graphviz's Dot language
========================================================

.. image:: https://pypip.in/py_versions/pydotplus/badge.png
   :target: https://pypi.python.org/pypi/pydotplus/
   :alt: Supported Python versions

.. image:: https://pypip.in/version/pydotplus/badge.png?text=version
   :target: https://pypi.python.org/pypi/pydotplus/
   :alt: Latest Version

.. image:: https://pypip.in/download/pydotplus/badge.png
   :target: https://pypi.python.org/pypi/pydotplus/
   :alt: Downloads

.. image:: https://pypip.in/license/pydotplus/badge.png
   :target: https://pypi.python.org/pypi/pydotplus/
   :alt: License

.. image:: https://pypip.in/status/pydotplus/badge.png
   :target: https://pypi.python.org/pypi/pydotplus/
   :alt: Status

.. image:: https://travis-ci.org/carlos-jenkins/pydotplus.svg?branch=master
   :target: https://travis-ci.org/carlos-jenkins/pydotplus
   :alt: Continuous Integration

.. image:: https://coveralls.io/repos/carlos-jenkins/pydotplus/badge.png
   :target: https://coveralls.io/r/carlos-jenkins/pydotplus
   :alt: Coverage


About
=====

Py3DotPlus is an improved version of the old pydot project that provides a
Python Interface to Graphviz's Dot language.

   http://pydotplus.readthedocs.org/

Differences with pydotplus:

- Python 3.8 compatible.


Installation
============

::

   pip install py3dotplus


Development
===========

   https://github.com/carlos-jenkins/pydotplus

Run code QA:

::

   pip install tox
   tox


Documentation
=============

User guide and API Reference can be found in:

   http://pydotplus.readthedocs.org/

To build it from source execute:

::

   pip install sphinx sphinx_rtd_theme
   cd doc/
   make html


Requirements
============

- ``pyparsing``: pydot requires the pyparsing module in order to be able to
  load DOT files.

- ``GraphViz``: is needed in order to render the graphs into any of the
  plethora of output formats supported.


License
=======

This code is distributed under the MIT license. See LICENSE for details.
