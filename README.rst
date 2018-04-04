Python pastebin wrapper
=======================

Simple python wrapper to work with https://pastebin.com/ service. Library are using pastebin API available `here <https://pastebin.com/api>`_.

Basic example:

.. code-block:: python

    >>> import pastebiner
    >>> p = pastebiner.Pastebin(dev_key='xxx')
    >>> p.login('user', 'pass')
    >>> p.create('print("hello world!")', "My first pastebin", p.FORMAT_PYTHON)
    'https://pastebin.com/41j5hgXu'


Installation
------------

To install pastebin-python, simply use `pip` such as:

.. code-block:: bash

    $ pip install pastebiner
 
Documentation
-------------

You can read the documentation at https://readthedocs.org/pastebin-python/