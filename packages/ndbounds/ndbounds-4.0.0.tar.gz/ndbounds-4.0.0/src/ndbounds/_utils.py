# Copyright (C) 2021 Matthias Nadig

import numpy as np


def _flatten_component(bounds_component):
    """ Flattens the array except for the last axis -> output shape is (None, n_dims) """
    if bounds_component.ndim == 1:
        # Singular bound
        return bounds_component
    else:
        return np.reshape(bounds_component, (-1, bounds_component.shape[-1]))


def _copy_if_required(arr, copy):
    """ Returns either the input array or a copy of it, depending on the copy-flag """
    if copy:
        return np.copy(arr)
    else:
        return arr
