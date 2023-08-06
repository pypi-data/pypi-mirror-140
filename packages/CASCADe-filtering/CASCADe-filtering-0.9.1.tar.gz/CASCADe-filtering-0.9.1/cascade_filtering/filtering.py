#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 13:59:44 2022

@author: bouwman
"""
import numpy as np
from typing import Tuple
import copy
import warnings

from cascade_filtering.stencil import filter_image_cube_ufunc as filter_image_cube

__all__ = ['prepare_data_for_filtering', 'DirectionalFilter']


def prepare_data_for_filtering(
   image_cube: np.ndarray, mask_cube: np.ndarray, uncertainty_cube: np.array,
   kernel_stack_shape: tuple, ROI=None) -> Tuple[np.ndarray, np.ndarray,
                                                 np.array, tuple, tuple, tuple]:
    """
    Preprocess input data for filtering.

    Parameters
    ----------
    image_cube : np.ndarray
        Spectral image cube.
    mask_cube : 'np.ndarray' of 'bool'
        Pixel mask indicating valid data
    uncertainty_cube : np.array
        Uncertainty estimate per pixel
    kernel_stack_shape : tuple
        Shape of the convolution kernel
    ROI : TYPE, optional
        Region of interest. The default is None.

    Returns
    -------
    adjusted_image_cube : TYPE
        zero padded spectral image cube
    adjusted_mask_cube : np.array of np.int8
        zero padded pixel mask
    adjusted_uncertainty_cube : np.array
        zero padded uncertainty cube
    sub_image_idex : TYPE
        DESCRIPTION.
    valid_pp_data_index : TYPE
        DESCRIPTION.
    valid_filtered_data_index : TYPE
        DESCRIPTION.

    """
    if ROI is None:
        adjusted_image_cube = image_cube
        adjusted_mask_cube = mask_cube
        adjusted_uncertainty_cube = uncertainty_cube
        sub_image_idex = np.ix_(np.ones((image_cube.shape[0]), dtype=bool),
                                np.ones((image_cube.shape[1]), dtype=bool),
                                np.ones((image_cube.shape[2]), dtype=bool))
    else:
       sub_image_idex = \
           np.ix_(np.arange(image_cube.shape[0]), (~ROI).any(1), (~ROI).any(0))
       adjusted_image_cube = image_cube[sub_image_idex]
       adjusted_uncertainty_cube = uncertainty_cube[sub_image_idex]
       adjusted_mask_cube = mask_cube[sub_image_idex]

    if len(kernel_stack_shape) == 3:
         KHWz = 0
         KHWy = kernel_stack_shape[1]//2
         KHWx = kernel_stack_shape[2]//2
    elif len(kernel_stack_shape) == 4:
        KHWz = kernel_stack_shape[1]//2
        KHWy = kernel_stack_shape[2]//2
        KHWx = kernel_stack_shape[3]//2
    else:
        raise ValueError("Kernel shape not valid")

    adjusted_image_cube = \
        np.pad(adjusted_image_cube, ((KHWz, KHWz),(KHWy, KHWy), (KHWx, KHWx)),
               'constant', constant_values=0.0)
    adjusted_uncertainty_cube = \
        np.pad(adjusted_uncertainty_cube, ((KHWz, KHWz),(KHWy, KHWy), (KHWx, KHWx)),
               'constant', constant_values=0.0)
    adjusted_mask_cube = \
        np.pad(adjusted_mask_cube, ((KHWz, KHWz),(KHWy, KHWy), (KHWx, KHWx)),
               'constant', constant_values=True)
    adjusted_mask_cube = (~adjusted_mask_cube).astype(np.int8)
    
    adjusted_data_shape = adjusted_mask_cube.shape
    
    valid_filtered_data_index = np.ix_(np.arange(kernel_stack_shape[0]),
                                       np.arange(KHWz, adjusted_data_shape[0]-KHWz),
                                       np.arange(KHWy, adjusted_data_shape[1]-KHWy),
                                       np.arange(KHWx, adjusted_data_shape[2]-KHWx))
    valid_pp_data_index = np.ix_(np.arange(KHWz, adjusted_data_shape[0]-KHWz),
                                 np.arange(KHWy, adjusted_data_shape[1]-KHWy),
                                 np.arange(KHWx, adjusted_data_shape[2]-KHWx))
    
    return (adjusted_image_cube, adjusted_mask_cube, adjusted_uncertainty_cube,
            sub_image_idex, valid_pp_data_index, valid_filtered_data_index)



class DirectionalFilter:
    """
    Directional Filter Class.
    
    #should hold the filter kernesls, either on creation or with load_kernel()
    # need sigma for clip
    #should filter the data when callling filter() this includes iteration.
    #     procedure: filter image cube
    #                filter squared image cube
    #                determine variance
    #                determine minimum variance
    #                determine deviating pixels
    #                update image_cube and mask
    #                iterate untill converged.
    """

    def __init__(self, directional_filter_kernels=None, sigma=8.0,
                 acceptance_treshold=0.01, max_iterations=20):
        self.filter_kernels = directional_filter_kernels
        self.sigma = sigma
        self.acceptance_treshold = acceptance_treshold
        self.max_iterations = max_iterations

    def load_filter_kernels(self, directional_filter_kernels):
        self.filter_kernels = directional_filter_kernels
        self.check_filter_kernels()

    def set_acceptance_treshold(self, acceptance_treshold):
        self.acceptance_treshold = acceptance_treshold
    
    def set_max_iterations(self, max_iterations):
        self.max_iterations = max_iterations

    def run_filter(self, image_cube, image_cube_mask, image_cube_error, ROI=None):
        """
        

        Parameters
        ----------
        image_cube : 'nd.array' of 'flaot'
            spectral image cube
        image_cube_mask : 'nd.array' of 'bool'
            pixel mask
        image_cube_error : 'nd.array' or 'float'
            pixel uncertainty.
        ROI : 'nd.array' of 'bool', optional
            Region of interest. The default is None.

        Returns
        -------
        None.

        """
        self.check_filter_kernels()
        self.check_data(image_cube, image_cube_mask, ROI=ROI)
        
        # pp data is used to store filered data
        # need a copy of the original mask to store flaged pixels
        (self.pp_image_cube, self.pp_image_cube_mask, self.pp_image_cube_error,
         self.pp_roi_image_cube_index , self.pp_data_cube_valid_index,
         self.filtered_data_valid_index) = \
            prepare_data_for_filtering(image_cube, image_cube_mask,
                                       image_cube_error,
                                       self.filter_kernels.shape, ROI=ROI)
        
        self.cumulative_image_cube_mask = copy.copy(self.pp_image_cube_mask)
        
        self.number_of_flagged_pixels = \
            np.sum(self.pp_image_cube_mask[self.pp_data_cube_valid_index] == 0)
  
        self.acceptance_limit = \
            np.min([int(self.acceptance_treshold * \
                self.pp_image_cube[self.pp_data_cube_valid_index].size),
                    self.number_of_flagged_pixels])

        iiteration = 1
        while ((self.number_of_flagged_pixels  > self.acceptance_limit) & \
                 (iiteration <= self.max_iterations)) | (iiteration == 1):
            print(f"iteration: {iiteration}, number of flagged pixel: {self.number_of_flagged_pixels}")
            # find bad pixels
            self.apply_filter()
            self.analyze_variance()
            self.sigma_clip()
            # second pass with bad pixels flagged to get better mean.
            self.apply_filter()
            self.analyze_variance()
            # clean data
            self.clean_image_cube()
                     
            iiteration += 1
        if (iiteration > self.max_iterations) & \
                 (self.number_of_flagged_pixels < self.acceptance_limit):
             warnings.warn("Iteration not converged in "
                           "iterative_bad_pixel_flagging. {} mask values not "
                           "converged. An increase of the maximum number of "
                           "iteration steps might be advisable.".
                           format(self.number_of_flagged_pixels-self.acceptance_limit))

    @staticmethod
    def check_data(image_cube, image_cube_mask, ROI=None):
        """
        

        Parameters
        ----------
        image_cube : TYPE
            DESCRIPTION.
        image_cube_mask : TYPE
            DESCRIPTION.
        ROI : TYPE, optional
            DESCRIPTION. The default is None.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if (image_cube.shape != image_cube_mask.shape):
            raise ValueError("Data cube and data mask do not have the same size.")
        if (image_cube.ndim != 3):
            raise ValueError("Data not an image cube.")
        if not (ROI is None):
            if ROI.shape != image_cube.shape[1:]:
                raise ValueError("ROI and data cube not compatable")
     
    def check_filter_kernels(self):
        """
        

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if self.filter_kernels is None:
            raise ValueError("No filter kernels loaded.")
        if (not self.filter_kernels.ndim in [3, 4]):
            raise ValueError("Filter kernel steck needs to be 3d or 4d.")     
        if (self.filter_kernels.shape[-2] != self.filter_kernels.shape[-1]):
            raise ValueError("Filter kernel needs to be square.")
        if self.filter_kernels.ndim == 4:
            if (self.filter_kernels.shape[-3] != self.filter_kernels.shape[-1]):
                raise ValueError("Filter kernel needs to be a cube.")
        if (self.filter_kernels.shape[-2]%2 -1):
            raise ValueError("Filter kernel width needs to be odd.")
 
    def apply_filter(self):
        """
        

        Returns
        -------
        None.

        """
        self.filtered_image_cube = \
            filter_image_cube(self.pp_image_cube,
                              self.pp_image_cube_mask,
                              self.filter_kernels)
        self.filtered_image_cube_square = \
            filter_image_cube(self.pp_image_cube**2,
                              self.pp_image_cube_mask,
                              self.filter_kernels)
    
    def analyze_variance(self):
        """
        

        Returns
        -------
        None.

        """
        variance = self.filtered_image_cube_square - self.filtered_image_cube**2
        
        valid_mask = np.ones_like(variance, dtype=bool)
        valid_mask[self.filtered_data_valid_index] = False
        I = np.ma.argmin(np.ma.array(variance, mask=valid_mask), axis=0)
        self.index_optimal_filter_kernel = \
             (I,) + np.ix_(*[np.arange(i) for i in variance.shape[1:]])
            
        self.optimal_filtered_image_cube = \
            self.filtered_image_cube[self.index_optimal_filter_kernel]
        self.optimal_filtered_variance = variance[self.index_optimal_filter_kernel]

    def clean_image_cube(self):
        """
        

        Returns
        -------
        None.

        """
        self.cumulative_image_cube_mask *= self.pp_image_cube_mask
        mask = self.pp_image_cube_mask == 0
        self.pp_image_cube[mask] = \
            self.optimal_filtered_image_cube[mask]
        self.pp_image_cube_error[mask] = \
            np.sqrt(self.optimal_filtered_variance[mask])
        mask_temp = self.pp_image_cube_mask[self.pp_data_cube_valid_index]
        mask_temp[mask[self.pp_data_cube_valid_index]] = 1
        self.pp_image_cube_mask[self.pp_data_cube_valid_index] = mask_temp
        

    def sigma_clip(self):
        """
        

        Returns
        -------
        None.

        """
        mask = ((self.pp_image_cube-self.optimal_filtered_image_cube)**2 > 
                (self.sigma * self.optimal_filtered_variance) + np.finfo(float).resolution)
        self.number_of_flagged_pixels = np.sum(mask)
        self.pp_image_cube_mask[mask] = 0