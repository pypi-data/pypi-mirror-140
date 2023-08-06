.. _loggdet:

******
logdet
******

Compute the logdet of a non-singular matrix.

.. math::

    \frac{\partial^n H^{(k)}_{\nu}(z)}{\partial z^n},

where

* :math:`n \in \mathbb{N}` is the order of the derivative (:math:`n = 0` indicates no derivative).
* :math:`k` can be :math:`1` or :math:`2` and indicates the Hankel function of the first or second type, respectively.
* :math:`\nu \in \mathbb{R}` is the order of the Bessel function.
* :math:`z \in \mathbb{C}` is the input argument.
  

======
Syntax
======

This function has the following syntaxes depending on whether it is used in Python or Cython, or the input argument ``z`` is complex or real.

+------------+-----------------+------------------------------------------------------------------------+
| Interface  | Input Type      | Function Signature                                                     |
+============+=================+========================================================================+
| **Python** | Real or Complex | ``besselh(nu, k, z, n=0)``                                             |
+------------+-----------------+------------------------------------------------------------------------+
| **Cython** | Real            | ``double complex besselh(double nu, int k, double z, int n)``          |
+            +-----------------+------------------------------------------------------------------------+
|            | Complex         | ``double complex cbesselh(double nu, int k, double complex z, int n)`` |
+------------+-----------------+------------------------------------------------------------------------+

**Input Arguments:**

.. attribute:: sym_pos
   :type: boolean

    If `True`, the matrix `A` is assumed to be symmetric and positive-definite
    (SPD). This can be as twice as faster as when the matrix is not SPD. If set
    to `False`, the matrix is assumed to be generic.

.. seealso::

   * :ref:`loggdet <loggdet>`: Log of determinant terms used in Gaussian
     process regression.
   * :ref:`logpdet <logpdet>`: Log of pseudo-determinant of presicion matrix in
     Gaussian process regression.


========
Examples
========
 
--------------------
Using in Cython Code
--------------------

The codes below should be used in a ``.pyx`` file and compiled with Cython.

As shown in the codes below, the python's global lock interpreter, or ``gil``, can be optionally released inside the scope of ``with nogil:`` statement. This is especially useful in parallel OpenMP environments.

~~~~~~~~~~
Real Input
~~~~~~~~~~

This example shows the real function ``besselh`` to compute the Bessel function of the third kind for a real argument ``z``. The output variables ``d0h``, ``d1h``, and ``d2h`` are complex variables and represent the values of Bessel function and its first and second derivatives, respectively.

.. code-block:: python

    >>> import numpy
    >>> from detkit import logdet

    >>> # Generate a random matrix
    >>> n = 20
    >>> A = numpy.random.randn(n, n)

    >>> # Compute logdet of generic matrix
    >>> logdet_ = logdet(A)

    >>> # Compute logdet of symmetric and positive-definite matrix
    >>> B = A.T @ A
    >>> logdet_ = logdet(A, sym_pos=True)


=========
Algorithm
=========

Depending on the values of the input parameters :math:`(\nu, z, n)`, one of the following two algorithms is employed.

* If :math:`\nu + \frac{1}{2} \in \mathbb{Z}`, the Bessel function is computed using :ref:`half-integer formulas <half_int_besselh>` in terms of elementary functions.
* For other cases, the computation is carried out by Amos Fortran library (see [Amos-1986]_) using ``zbesh`` subroutine in that library.

-------------
Special Cases
-------------

In the special cases below, the computation is performed by taking advantage of some of the known formulas and properties of the Bessel functions.

~~~~~~~~~~~~~~~~~~~~
Negative :math:`\nu`
~~~~~~~~~~~~~~~~~~~~

When :math:`\nu < 0` and for the two cases below, the Bessel function is related to the Bessel function of the positive parameter :math:`-\nu`.

* If :math:`\nu \in \mathbb{Z}` (see [DLMF]_ Eq. `10.4.1 <https://dlmf.nist.gov/10.4#E1>`_):

  .. math::

      H^{(k)}_{\nu}(z) = (-1)^{\nu} H^{(k)}_{-\nu}(z),

  where :math:`k = 1, 2`.

* If :math:`\nu + \frac{1}{2} \in \mathbb{Z}` (see [DLMF]_ Eq. `10.2.3 <https://dlmf.nist.gov/10.2#E3>`_):

  .. math::

      H^{(k)}_{\nu}(z) = \left( \cos(\pi \nu) - i \alpha(k) \sin(\pi \nu) \right) H^{(k)}_{-\nu}(z),

  where :math:`k = 1, 2`, :math:`\alpha(1) = 1`, and :math:`\alpha(2) = -1`.

~~~~~~~~~~~
Derivatives
~~~~~~~~~~~

If :math:`n > 0`, the following relation for the derivative is applied (see [DLMF]_ Eq. `10.6.7 <https://dlmf.nist.gov/10.6#E7>`_):

.. math::
   
   \frac{\partial^n H^{(k)}_{\nu}(z)}{\partial z^n} = \frac{1}{2^n} \sum_{i = 0}^n (-1)^i \binom{n}{i} H^{(k)}_{\nu - n + 2i}(z),

where :math:`k = 1, 2`.

.. _half_int_besselh:

~~~~~~~~~~~~~~~~~~~~~~~~
Half-Integer :math:`\nu`
~~~~~~~~~~~~~~~~~~~~~~~~

When :math:`\nu` is half-integer, the Bessel function is computed in terms of elementary functions as follows.

* If :math:`z = 0`, then ``NAN`` is returned.

* If :math:`z < 0` and :math:`z \in \mathbb{R}`, then ``NAN`` is returned.

* If :math:`\nu = \pm \frac{1}{2}` (see [DLMF]_ Eq. `10.16.1 <https://dlmf.nist.gov/10.16#E1>`_)

  .. math::

      H^{(k)}_{\frac{1}{2}}(z) = \sqrt{\frac{2}{\pi z}} \left( \sin(z) - i \alpha(k) \cos(z) \right), \\
      H^{(k)}_{-\frac{1}{2}}(z) = \sqrt{\frac{2}{\pi z}} \left( \cos(z) + i \alpha(k) \sin(z) \right),

  where :math:`k = 1, 2` and :math:`\alpha(1) = 1` and :math:`\alpha(2) = -1`. Depending on :math:`z`, the above relations are computed using the real or complex implementation of the elementary functions.

* Higher-order half-integer parameter :math:`\nu` is related to the above relation for :math:`\nu = \pm \frac{1}{2}` using recursive formulas (see [DLMF]_ Eq. `10.6.1 <https://dlmf.nist.gov/10.6#E1>`_):

.. math::

    H^{(k)}_{\nu}(z) = \frac{2 (\nu - 1)}{z} H^{(k)}_{\nu - 1}(z) - H^{(k)}_{\nu - 2}(z), \qquad \nu > 0, \\
    H^{(k)}_{\nu}(z) = \frac{2 (\nu + 1)}{z} H^{(k)}_{\nu + 1}(z) - H^{(k)}_{\nu + 2}(z), \qquad \nu < 0,

where :math:`k = 1, 2`.


==========
References
==========

.. [Ameli-2022] Ameli, S., Shadden, S. C. (2022) A Singular Woodbury and Pseudo-Determinant Matrix Identities and Application to Gaussian Process Regression.

