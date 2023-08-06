/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


// =======
// Headers
// =======

#include "./c_matrix_decompositions.h"
#include <cmath>  // sqrt
#include "../_c_basic_algebra/c_vector_operations.h"  // cVectorOperations
#include "../_definitions/definitions.h"


// ==
// lu
// ==

/// \brief LU decomposition (no pivoting). A and L are (n, n) matrices.
///

template <typename DataType>
void cMatrixDecompositions<DataType>::lu(
        DataType* A,
        const LongIndexType num_rows,
        DataType* L)
{
    LongIndexType i;
    LongIndexType j;
    LongIndexType k;

    // Initialize L as the Identity matrix
    for(i=0; i < num_rows; ++i)
    {
        for (j=0; j < num_rows; ++j)
        {
            if (i == j)
            {
                L[i*num_rows + j] = 1.0;
            }
            else
            {
                L[i*num_rows + j] = 0.0;
            }
        }
    }

    // LU Decomposition
    for (k=0; k < num_rows; ++k)
    {
        for (i=k+1; i < num_rows; ++i)
        {
            L[i*num_rows + k] = A[i*num_rows + k] / A[k*num_rows + k];
        }

        for (j=k+1; j < num_rows; ++j)
        {
            for (i=0; i < num_rows; ++i)
            {
                A[j*num_rows + i] -= L[j*num_rows + k] * A[k*num_rows + i];
            }
        }
    }
}


// ===
// lup
// ===

/// \brief LUP decomposition (with partial pivoting). A is (n, n) matrix and
///        P is a 1D array of size n+1.
///

template <typename DataType>
FlagType cMatrixDecompositions<DataType>::lup(
        DataType* A,
        LongIndexType* P,
        const LongIndexType num_rows,
        const DataType tol)
{
    LongIndexType i;
    LongIndexType j;
    LongIndexType k;
    LongIndexType imax;

    DataType maxA;
    DataType absA;

    for (i = 0; i <= num_rows; ++i)
    {
        //Unit permutation matrix, P[num_rows] initialized with num_rows
        P[i] = i;
    }

    for (i = 0; i < num_rows; ++i)
    {
        maxA = 0.0;
        imax = i;

        for (k = i; k < num_rows; k++)
        {
            if ((absA = fabs(A[P[k]*num_rows + i])) > maxA)
            {
                maxA = absA;
                imax = k;
            }
        }

        if (maxA < tol)
        {
            //failure, matrix is degenerate
            return 1;
        }

        if (imax != i)
        {
            // pivoting P
            j = P[i];
            P[i] = P[imax];
            P[imax] = j;

            // counting pivots starting from num_rows (for determinant)
            P[num_rows]++;
        }

        for (j = i+1; j < num_rows; ++j)
        {
            A[P[j]*num_rows + i] /= A[P[i]*num_rows + i];

            for (k = i+1; k < num_rows; ++k)
            {
                A[P[j]*num_rows + k] -= \
                    A[P[j]*num_rows + i] * A[P[i]*num_rows + k];
            }
        }
    }

    return 0;
}


// ========
// cholesky
// ========

/// \brief Cholesky decompositon using Banachiewicz algorithm.
///

template <typename DataType>
FlagType cMatrixDecompositions<DataType>::cholesky(
        DataType* A,
        const LongIndexType num_rows,
        DataType* L)
{
    LongIndexType i;
    LongIndexType j;
    LongIndexType k;
    DataType residual;

    // Initialize L as zero matrix
    for (i=0; i < num_rows; ++i)
    {
        for (j=0; j < num_rows; ++j)
        {
            L[i*num_rows + j] = 0.0;
        }
    }
   
    DataType sum;

    for (i = 0; i < num_rows; ++i)
    {
        for (j = 0; j <= i; ++j)
        {
            sum = 0;

            if (j == i)
            {
                for (k=0; k < j; ++k)
                {
                    sum += L[j*num_rows + k] * L[j*num_rows + k];
                }

                residual = A[j*num_rows + j] - sum;
                if (residual < 0.0)
                {
                    // Cholesky decompositon fails. Matrix seems not to be
                    // positive-definite.
                    return 1;
                }

                L[j*num_rows + j] = sqrt(residual);
            }
            else
            {
                for (k=0; k < j; ++k)
                {
                    sum += L[i*num_rows + k] * L[j*num_rows + k];
                }

                L[i*num_rows + j] = (A[i*num_rows + j] - sum) / \
                                    L[j*num_rows + j];
            }
        }
    }

    return 0;
}


// ============
// gram schmidt
// ============

/// \brief Gram-Schmidt orthogonalization. The input matrix \c A will be
///        overwritten.

template <typename DataType>
void cMatrixDecompositions<DataType>::gram_schmidt(
        DataType *A,
        const LongIndexType num_rows,
        const LongIndexType num_columns)
{
    DataType inner_prod;

    // Iterate over vectors
    for (LongIndexType i=0; i < num_columns; ++i)
    {
        for (LongIndexType j=0; j < i; ++j)
        {
            // Inner product of i-th and j-th columns of matrix A
            inner_prod = cVectorOperations<DataType>::inner_product(
                    A, num_rows, num_columns, j, i);

            // Subtraction
            cVectorOperations<DataType>::subtract_scaled_vector(
                    A, num_rows, num_columns, inner_prod, j, i);
        }

        // Normalize i-th column
        cVectorOperations<DataType>::normalize_vector_in_place(
                A, num_rows, num_columns, i);
    }
}


// ===============================
// Explicit template instantiation
// ===============================

template class cMatrixDecompositions<float>;
template class cMatrixDecompositions<double>;
template class cMatrixDecompositions<long double>;
