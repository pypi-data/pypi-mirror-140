===============
interval-search
===============


.. image:: https://img.shields.io/pypi/v/interval-search.svg
        :target: https://pypi.python.org/pypi/interval-search

.. image:: https://img.shields.io/travis/mmore500/interval-search.svg
        :target: https://travis-ci.com/mmore500/interval-search

.. image:: https://readthedocs.org/projects/interval-search/badge/?version=latest
        :target: https://interval-search.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




interval-search provides predicate-based binary and doubling search implementations


* Free software: MIT license
* Documentation: https://interval-search.readthedocs.io.


.. code-block:: python3

  import interval_search as inch



  # inch.binary_search
  list_ = [1, 10, 20, 500, 5000]
  binary_search(lambda x: list_[x] >= 20, 0, len(list_) - 1)
  # -> 2

  # inch.doubling_search
  inch.doubling_search(lambda x: x >= 5) # -> 5
  # with a lower bound to start searching at,
  inch.doubling_search(lambda x: x >= 5, 10) # -> 10

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
