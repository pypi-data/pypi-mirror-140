# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import numpy
from .._definitions.types cimport LongIndexType, FlagType
from .benchmark cimport Benchmark

# To avoid cython's bug that does not recognizes "long double" in template []
ctypedef long double long_double

__all__ = ['get_instructions_per_task']


# =========================
# get instructions per task
# =========================

cpdef get_instructions_per_task(task='matmat', dtype='float64'):
    """
    Counts the hardware instructions on the current device to compute a single
    flop of a benchmark task. 

    Parameters
    ----------
        task : {'matmat', 'gramian', 'cholesky', 'lu', 'lup'}, default='matmat'
            The benchmark task to count its hardware instructions.
            * ``'matmat'``: matrix-matrix multiplication task.
            * ``'gramian'``: Gramian matrix-matrix multiplication task.
            * ``'cholesky'``: Cholesky decomposition task.
            * ``'lu'``: LU decomposition task.
            * ``'lu'``: LUP decomposition task.

        dtype : {'float32', 'float64', 'float128'}, default='float64'
            The type of the test data.

    Returns
    -------

        inst : int
            Count of hardware instructions

    Notes
    -----
    """

    n = (1.0 / numpy.linspace(1.0/30.0, 1.0/500.0, 10) + 0.5).astype(int)
    inst_per_task = -numpy.ones((n.size, ), dtype=float)

    for i in range(n.size):

        if dtype == 'float32':
            inst = _get_instructions_float(task, n[i])
        elif dtype == 'float64':
            inst = _get_instructions_double(task, n[i])
        elif dtype == 'float128':
            inst = _get_instructions_long_double(task, n[i])
        else:
            raise ValueError('"dtype" should be "float32", "float64", or ' +
                             '"float128".')

        # Negative means the perf_tool is not installed on Linux OS.
        if inst < 0:
            return numpy.nan

        # Flops for matrix-matrix multiplication
        matmat_flops = n[i]**3
        inst_per_task[i] = inst / matmat_flops

    # Find inst_per_task when n tends to infinity using an exponential model
    # inst_per_task = a/n + b
    coeff = numpy.polyfit(1.0/n, inst_per_task, deg=1)

    # In the limit n=infinity, b is the number of inst_per_task
    inst_per_task_limit = coeff[1]

    return inst_per_task_limit


# ======================
# get instructions float
# ======================

cpdef long long _get_instructions_float(
        task,
        int n):
    """
    Specialized for float type.
    """

    # A c-pointer just to specialize the template function to float
    cdef float* dummy_var = NULL
    cdef long long inst = -1

    if task == 'matmat':
        inst = Benchmark[float].matmat(dummy_var, n)
    elif task == 'gramian':
        inst = Benchmark[float].gramian(dummy_var, n)
    elif task == 'cholesky':
        inst = Benchmark[float].cholesky(dummy_var, n)
    elif task == 'lu':
        inst = Benchmark[float].lu(dummy_var, n)
    elif task == 'lup':
        inst = Benchmark[float].lup(dummy_var, n)
    else:
        raise ValueError('"task" is not recognized.')

    return inst


# =======================
# get instructions double
# =======================

cpdef long long _get_instructions_double(
        task,
        int n):
    """
    Specialized for double type.
    """

    # A c-pointer just to specialize the template function to double
    cdef double* dummy_var = NULL
    cdef long long inst = -1

    if task == 'matmat':
        inst = Benchmark[double].matmat(dummy_var, n)
    elif task == 'gramian':
        inst = Benchmark[double].gramian(dummy_var, n)
    elif task == 'cholesky':
        inst = Benchmark[double].cholesky(dummy_var, n)
    elif task == 'lu':
        inst = Benchmark[double].lu(dummy_var, n)
    elif task == 'lup':
        inst = Benchmark[double].lup(dummy_var, n)
    else:
        raise ValueError('"task" is not recognized.')

    return inst


# ============================
# get instructions long double
# ============================

cpdef long long _get_instructions_long_double(
        task,
        int n):
    """
    Specialized for long double type.
    """

    # A c-pointer just to specialize the template function to long double
    cdef long double* dummy_var = NULL
    cdef long long inst = -1

    if task == 'matmat':
        inst = Benchmark[long_double].matmat(dummy_var, n)
    elif task == 'gramian':
        inst = Benchmark[long_double].gramian(dummy_var, n)
    elif task == 'cholesky':
        inst = Benchmark[long_double].cholesky(dummy_var, n)
    elif task == 'lu':
        inst = Benchmark[long_double].lu(dummy_var, n)
    elif task == 'lup':
        inst = Benchmark[long_double].lup(dummy_var, n)
    else:
        raise ValueError('"task" is not recognized.')

    return inst
