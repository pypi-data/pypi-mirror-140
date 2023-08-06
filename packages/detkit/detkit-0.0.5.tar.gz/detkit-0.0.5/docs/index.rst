******
detkit
******

|licence| |docs|

This package provides both Python and Cython interfaces for Bessel functions and a few other special functions. 

.. toctree::
    :maxdepth: 1
    :caption: Documentation
    :hidden:

    modules<_modules/detkit>

========
Features
========

* **Lightweight:** This package requires *no python dependency* at runtime.
* **Cython interface:** Both Python and Cython interfaces are available.
* **Releasing GIL:** Most importantly, the functions can be used in ``with nogil:`` environment, which is essential in parallel OpenMP applications with Cython.


====================
Interactive Tutorial
====================

|binder|

Launch an online interactive tutorial in `Jupyter notebook <https://mybinder.org/v2/gh/ameli/detkit/HEAD?filepath=notebooks%2FSpecial%20Functions.ipynb>`_.

=====
Links
=====

* `Package on Anaconda Cloud <https://anaconda.org/s-ameli/detkit>`_
* `Package on PyPi <https://pypi.org/project/detkit/>`_
* `Source code on Github <https://github.com/ameli/detkit>`_

.. * `Interactive Jupyter notebook <https://mybinder.org/v2/gh/ameli/detkit/HEAD?filepath=notebooks%2FSpecial%20Functions.ipynb>`_.
.. * `API <https://ameli.github.io/detkit/_modules/modules.html>`_

=================
How to Contribute
=================

We welcome contributions via `Github's pull request <https://github.com/ameli/detkit/pulls>`_. If you do not feel comfortable modifying the code, we also welcome feature request and bug report as `Github issues <https://github.com/ameli/detkit/issues>`_.

================
Related Packages
================

* `scipy.special <https://docs.scipy.org/doc/scipy/reference/special.html>`_: Many special functions are available in *scipy.special* package.
* `Gaussian Process <https://github.com/ameli/gaussian-process-param-estimation>`_: A python package that makes use of ``detkit``.


================
Acknowledgements
================

* National Science Foundation #1520825
* American Heart Association #18EIA33900046

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. |codecov-devel| image:: https://img.shields.io/codecov/c/github/ameli/detkit
   :target: https://codecov.io/gh/ameli/detkit
.. |docs| image:: https://github.com/ameli/detkit/workflows/docs/badge.svg
   :target: https://ameli.github.io/detkit/index.html
.. |licence| image:: https://img.shields.io/github/license/ameli/detkit
   :target: https://opensource.org/licenses/MIT
.. |travis-devel-linux| image:: https://img.shields.io/travis/com/ameli/detkit?env=BADGE=linux&label=build&branch=main
   :target: https://travis-ci.com/github/ameli/detkit
.. |travis-devel-osx| image:: https://img.shields.io/travis/com/ameli/detkit?env=BADGE=osx&label=build&branch=main
   :target: https://travis-ci.com/github/ameli/detkit
.. |travis-devel-windows| image:: https://img.shields.io/travis/com/ameli/detkit?env=BADGE=windows&label=build&branch=main
   :target: https://travis-ci.com/github/ameli/detkit
.. |implementation| image:: https://img.shields.io/pypi/implementation/detkit
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/detkit
.. |format| image:: https://img.shields.io/pypi/format/detkit
.. |pypi| image:: https://img.shields.io/pypi/v/detkit
   :target: https://pypi.org/project/special-functions/
.. |conda| image:: https://anaconda.org/s-ameli/detkit/badges/installer/conda.svg
   :target: https://anaconda.org/s-ameli/detkit
.. |platforms| image:: https://img.shields.io/conda/pn/s-ameli/detkit?color=orange?label=platforms
   :target: https://anaconda.org/s-ameli/detkit
.. |conda-version| image:: https://img.shields.io/conda/v/s-ameli/detkit
   :target: https://anaconda.org/s-ameli/detkit
.. |binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/ameli/detkit/HEAD?filepath=notebooks%2FSpecial%20Functions.ipynb
.. |downloads| image:: https://pepy.tech/badge/special-functions
   :target: https://pepy.tech/project/detkit
