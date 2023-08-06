#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 13:59:44 2022

@author: bouwman
"""

import numpy as np
import numba as nb

_all__ = ['stencil_kernel5', 'stencil_kernel7', 'stencil_kernel9',
          'stencil_kernel11', 'stencil_kernel5_3d', 'stencil_kernel7_3d',
          'stencil_kernel9_3d','stencil_kernel11_3d'
          'filter_image_cube', 'stencil_kernel_ufunc',
          'filter_image_cube_ufunc', 'stencil_kernel_3d_ufunc',
          'IMPLEMENTED_KERNEL_SIZES',]

IMPLEMENTED_KERNEL_SIZES = [5,7,9,11,19]

@nb.stencil(neighborhood = ((-2, 2),(-2, 2)), standard_indexing=("kernel",))
def stencil_kernel5(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-2, 3):
        for j in range(-2, 3):
            cumul_kernel += image[i, j] * mask[i, j] * kernel[i+2, j+2]
            norm_kernel += mask[i, j] * kernel[i+2, j+2]
    return cumul_kernel/norm_kernel

@nb.stencil(neighborhood = ((-2, 2),(-2, 2),(-2, 2)), standard_indexing=("kernel",))
def stencil_kernel5_3d(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-2, 3):
        for j in range(-2, 3):
            for k in range(-2, 3):
               cumul_kernel += image[i, j, k] * mask[i, j, k] * kernel[i+2, j+2, k+2]
               norm_kernel += mask[i, j, k] * kernel[i+2, j+2, k+2]
    return cumul_kernel/norm_kernel

@nb.stencil(neighborhood = ((-3, 3),(-3, 3)), standard_indexing=("kernel",))
def stencil_kernel7(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-3, 4):
        for j in range(-3, 4):
            cumul_kernel += image[i, j] * mask[i, j] * kernel[i+3, j+3]
            norm_kernel += mask[i, j] * kernel[i+3, j+3]
    return cumul_kernel/norm_kernel

@nb.stencil(neighborhood = ((-3, 3),(-3, 3),(-3, 3)), standard_indexing=("kernel",))
def stencil_kernel7_3d(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-3, 4):
        for j in range(-3, 4):
            for k in range(-3, 4):
               cumul_kernel += image[i, j, k] * mask[i, j, k] * kernel[i+3, j+3, k+3]
               norm_kernel += mask[i, j, k] * kernel[i+3, j+3, k+3]
    return cumul_kernel/norm_kernel


@nb.stencil(neighborhood = ((-4, 4),(-4, 4)), standard_indexing=("kernel",))
def stencil_kernel9(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-4, 5):
        for j in range(-4, 5):
            cumul_kernel += image[i, j] * mask[i, j] * kernel[i+4, j+4]
            norm_kernel += mask[i, j] * kernel[i+4, j+4]
    return cumul_kernel/norm_kernel

@nb.stencil(neighborhood = ((-4, 4),(-4, 4),(-4, 4)), standard_indexing=("kernel",))
def stencil_kernel9_3d(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-4, 5):
        for j in range(-4, 5):
            for k in range(-4, 5):
               cumul_kernel += image[i, j, k] * mask[i, j, k] * kernel[i+4, j+4, k+4]
               norm_kernel += mask[i, j, k] * kernel[i+4, j+4, k+4]
    return cumul_kernel/norm_kernel

@nb.stencil(neighborhood = ((-5, 5),(-5, 5)), standard_indexing=("kernel",))
def stencil_kernel11(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-5, 6):
        for j in range(-5, 6):
            cumul_kernel += image[i, j] * mask[i, j] * kernel[i+5, j+5]
            norm_kernel += mask[i, j] * kernel[i+5, j+5]
    return cumul_kernel/norm_kernel

@nb.stencil(neighborhood = ((-5, 5),(-5, 5),(-5, 5)), standard_indexing=("kernel",))
def stencil_kernel11_3d(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-5, 6):
        for j in range(-5, 6):
            for k in range(-5, 6):
               cumul_kernel += image[i, j, k] * mask[i, j, k] * kernel[i+5, j+5, k+5]
               norm_kernel += mask[i, j, k] * kernel[i+5, j+5, k+5]
    return cumul_kernel/norm_kernel

@nb.stencil(neighborhood = ((-8, 8),(-8, 8)), standard_indexing=("kernel",))
def stencil_kernel19(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-8, 9):
        for j in range(-8, 9):
            cumul_kernel += image[i, j] * mask[i, j] * kernel[i+8, j+8]
            norm_kernel += mask[i, j] * kernel[i+8, j+8]
    return cumul_kernel/norm_kernel

@nb.stencil(neighborhood = ((-8, 8),(-8, 8),(-8, 8)), standard_indexing=("kernel",))
def stencil_kernel19_3d(image, mask, kernel):
    """
    Numba kernel stencil.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    cumul_kernel = 0.0
    norm_kernel = 1.e-15
    for i in range(-8, 9):
        for j in range(-8, 9):
            for k in range(-8, 9):
               cumul_kernel += image[i, j, k] * mask[i, j, k] * kernel[i+8, j+8, k+8]
               norm_kernel += mask[i, j, k] * kernel[i+8, j+8, k+8]
    return cumul_kernel/norm_kernel


@nb.guvectorize(
    [(nb.float64[:, :], nb.int8[:, :], nb.float64[:, :], nb.float64[:, :])],
    '(m, n), (m, n), (k, k) -> (m, n)', cache=True, fastmath=True,
    nopython=True, target='parallel')
def stencil_kernel_ufunc(data, mask, kernel, filtered_data):
    """
    

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.
    filtered_data : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if kernel.shape[-1] == 5:
        filtered_data[:] = stencil_kernel5(data, mask, kernel)
    elif kernel.shape[-1] == 7:
        filtered_data[:] = stencil_kernel7(data, mask, kernel)
    elif kernel.shape[-1] == 9:
        filtered_data[:] = stencil_kernel9(data, mask, kernel)
    elif kernel.shape[-1] == 11:
        filtered_data[:] = stencil_kernel11(data, mask, kernel)    
    else:
        filtered_data[:] = stencil_kernel19(data, mask, kernel)

@nb.guvectorize(
    [(nb.float64[:, :, :], nb.int8[:, :, :], nb.float64[:, :, :], nb.float64[:, :, :])],
    '(l, m, n), (l, m, n), (k, k, k) -> (l, m, n)', cache=True, fastmath=True,
    nopython=True, target='parallel')
def stencil_kernel_3d_ufunc(data, mask, kernel, filtered_data):
    """
    

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    mask : TYPE
        DESCRIPTION.
    kernel : TYPE
        DESCRIPTION.
    filtered_data : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if kernel.shape[-1] == 5:
        filtered_data[:] = stencil_kernel5_3d(data, mask, kernel)
    elif kernel.shape[-1] == 7:
        filtered_data[:] = stencil_kernel7_3d(data, mask, kernel)
    elif kernel.shape[-1] == 9:
        filtered_data[:] = stencil_kernel9_3d(data, mask, kernel)
    elif kernel.shape[-1] == 11:
        filtered_data[:] = stencil_kernel11_3d(data, mask, kernel)    
    else:
        filtered_data[:] = stencil_kernel19_3d(data, mask, kernel)


@nb.jit(
        nopython=True, fastmath=True, parallel=True, cache=True)
def filter_image_cube(image_cube, mask_cube, kernel_stack):
    """
    Jitted image cube filter.

    Parameters
    ----------
    image_cube : TYPE
        DESCRIPTION.
    mask_cube : TYPE
        DESCRIPTION.
    kernel_stack : TYPE
        DESCRIPTION.

    Returns
    -------
    fitered_image : TYPE
        DESCRIPTION.

    """
    fitered_image = np.empty(kernel_stack.shape[0:1]+image_cube.shape)
    for k, kernel in enumerate(kernel_stack):
        for image, mask in zip(image_cube, mask_cube):
            if kernel_stack.ndim == 4:
                if kernel.shape[-1] == 5:
                    fitered_image[k, ...] = stencil_kernel5_3d(image, mask, kernel)
                elif kernel.shape[-1] == 7:
                    fitered_image[k, ...] = stencil_kernel7_3d(image, mask, kernel)
                elif kernel.shape[-1] == 9:
                    fitered_image[k, ...] = stencil_kernel9_3d(image, mask, kernel)
                elif kernel.shape[-1] == 11:
                    fitered_image[k, ...] = stencil_kernel11_3d(image, mask, kernel)    
                else:
                    fitered_image[k, ...] = stencil_kernel19_3d(image, mask, kernel)
            else:
                if kernel.shape[-1] == 5:
                    fitered_image[k, ...] = stencil_kernel5(image, mask, kernel)
                elif kernel.shape[-1] == 7:
                    fitered_image[k, ...] = stencil_kernel7(image, mask, kernel)
                elif kernel.shape[-1] == 9:
                    fitered_image[k, ...] = stencil_kernel9(image, mask, kernel)
                elif kernel.shape[-1] == 11:
                    fitered_image[k, ...] = stencil_kernel11(image, mask, kernel)   
                else:
                    fitered_image[k, ...] = stencil_kernel19(image, mask, kernel)
    return fitered_image


def filter_image_cube_ufunc(image_cube, mask_cube, kernel_stack):
    """
    Image cube filter.

    Parameters
    ----------
    image_cube : TYPE
        DESCRIPTION.
    mask_cube : TYPE
        DESCRIPTION.
    kernel_stack : TYPE
        DESCRIPTION.

    Returns
    -------
    fitered_image : TYPE
        DESCRIPTION.

    """
    if kernel_stack.ndim == 4:
        stencil_ufunc = stencil_kernel_3d_ufunc
    else:
        stencil_ufunc = stencil_kernel_ufunc
    
    fitered_image = np.empty(kernel_stack.shape[0:1]+image_cube.shape)
    for k, kernel in enumerate(kernel_stack):
        stencil_ufunc(image_cube, mask_cube, kernel, fitered_image[k, ...])
    return fitered_image
