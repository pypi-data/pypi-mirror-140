.. image:: https://coveralls.io/repos/github/btimby/mkpy224o/badge.svg?branch=master
    :target: https://coveralls.io/github/btimby/mkpy224o?branch=master

.. image:: https://github.com/btimby/mkpy224o/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/btimby/mkpy224o/actions

.. image:: https://badge.fury.io/py/mkpy224o.svg
    :target: https://badge.fury.io/py/mkpy224o

mkpy224o
========

Python wrapper for mkp224o CLI tool.

Installation
------------

To install the library:

``pip install mkpy224o``

This wrapper requires mkp224o in order to function. If you want to use regular expressions as filters, you will need to enable the regex feature (disabled by default).

.. code-block:: bash

    git clone git@github.com:cathugger/mkp224o.git
    cd mkp224o/
    ./autogen.sh
    ./configure --enable-regex=yes
    make
    sudo install mkp224o /usr/local/bin/mkp224o

Note that you can omit ``--enable-regex=yes`` if you don't want to use regular expressions and you can install to any destination that is in your ``PATH``.

Usage
-----

.. code-block:: python

    from mkpy224o import find_keys

    keys = find_keys('^foo', on_progress=print)

The above will find a key that starts with foo. Progress will be printed to the console.
