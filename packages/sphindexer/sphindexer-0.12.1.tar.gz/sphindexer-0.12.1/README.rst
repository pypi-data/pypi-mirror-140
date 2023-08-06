.. image:: https://readthedocs.org/projects/sphindexer/badge/?version=latest
   :target: https://sphindexer.readthedocs.io/en/latest/
   :alt: Documentation Status

.. image:: https://circleci.com/gh/KaKkouo/sphindexer.svg?style=shield
   :target: https://circleci.com/gh/KaKkouo/sphindexer
   :alt: Build Status (CircleCI)

.. image:: https://codecov.io/gh/KaKkouo/sphindexer/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/KaKkouo/sphindexer
   :alt: Code Coverage Status (Codecov)

.. image:: https://img.shields.io/badge/License-BSD%202--Clause-blue.svg
   :target: https://opensource.org/licenses/BSD-2-Clause
   :alt: BSD 2 Clause

A sphinx extension to replace the IndexEntries class.

- Sphindexer = Sphinx + Indexer

THE GOAL
--------
- It's to become the IndexEntries class.
- It has the extention for kana_text.

FEATURE
-------

- Even when editing glossary with index_key, make clean is not necessary.
- See/seealso appears at the first.
- When there are multiple functions with the same name, the first one will not be left out.
- It is relatively easy to customize the display order to your liking.

    - You must be able to develop sphinx extensions.

USAGE
-----

conf.py

.. code-block:: python

   extensions = ['sphindexer']

build ( without sphindexer ):

.. code-block:: sh

   $ make html 

build ( with sphindexer ):

.. code-block:: sh

   $ make idxr
