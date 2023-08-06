# Copyright (C) 2021 Matthias Nadig

import numpy as np


def _convert_se_to_cw(start, end, inplace=False):
    if inplace:
        center_prepared = start
        width_prepared = end
    else:
        center_prepared = np.empty(start.shape, dtype=start.dtype)
        width_prepared = np.empty(end.shape, dtype=end.dtype)

    width = np.subtract(end, start, out=width_prepared)
    center = np.add(start, np.multiply(0.5, width), out=center_prepared)

    return center, width


def _convert_cw_to_se(center, width, inplace=False):
    if inplace:
        start_prepared = center
        end_prepared = width
    else:
        start_prepared = np.empty(center.shape, dtype=center.dtype)
        end_prepared = np.empty(width.shape, dtype=width.dtype)

    width_half = np.multiply(0.5, width, out=end_prepared)
    start = np.subtract(center, width_half, out=start_prepared)
    end = np.add(center, width_half, out=end_prepared)

    return start, end


def _convert_se_to_sw(start, end, inplace=False):
    if inplace:
        width_prepared = end
    else:
        width_prepared = np.empty(end.shape, dtype=end.dtype)

    width = np.subtract(end, start, out=width_prepared)

    return start, width


def _convert_cw_to_sw(center, width, inplace=False):
    if inplace:
        start_prepared = center
    else:
        start_prepared = np.empty(center.shape, dtype=center.dtype)

    width_half = np.multiply(0.5, width)
    start = np.subtract(center, width_half, out=start_prepared)

    return start, width


def _convert_sw_to_se(start, width, inplace=False):
    if inplace:
        end_prepared = width
    else:
        end_prepared = np.empty(width.shape, dtype=width.dtype)

    end = np.add(start, width, out=end_prepared)

    return start, end


def _convert_sw_to_cw(start, width, inplace=False):
    if inplace:
        center_prepared = start
    else:
        center_prepared = np.empty(start.shape, dtype=start.dtype)

    width_half = np.multiply(0.5, width)
    center = np.add(start, width_half, out=center_prepared)

    return center, width


def _convert_array_se_to_cw(bounds):
    """
    Convert from (start, end) to (center, width)
    """

    bounds_new = np.empty(bounds.shape)
    bounds_new[..., 1] = np.subtract(bounds[..., 1], bounds[..., 0], out=bounds_new[..., 1])
    bounds_new[..., 0] = np.add(bounds[..., 0], np.multiply(0.5, bounds_new[..., 1]), out=bounds_new[..., 0])

    return bounds_new


def _convert_array_se_to_cw_inplace(bounds):
    """
    Convert from (start, end) to (center, width)
    CAVEAT: Inplace modification!
    """

    np.subtract(bounds[..., 1], bounds[..., 0], out=bounds[..., 1])
    np.add(bounds[..., 0], np.multiply(0.5, bounds[..., 1]), out=bounds[..., 0])

    return bounds


def _convert_array_se_to_sw(bounds):
    """
    Convert from (start, end) to (start, width)
    """
    return _convert_array_se_to_sw_inplace(np.copy(bounds))


def _convert_array_se_to_sw_inplace(bounds):
    """
    Convert from (start, end) to (start, width)
    CAVEAT: Inplace modification!
    """
    return np.subtract(bounds[..., 1], bounds[..., 0], out=bounds[..., 1])


def _convert_array_cw_to_se(bounds):
    """
    Convert from (center, width) to (start, end)
    """

    bounds_new = np.empty(bounds.shape)

    bounds_center = np.copy(bounds[..., 0])
    bounds_size_half = np.multiply(0.5, bounds[..., 1])

    bounds_new[..., 0] = np.subtract(bounds_center, bounds_size_half)
    bounds_new[..., 1] = np.add(bounds_center, bounds_size_half)

    return bounds_new


def _convert_array_cw_to_se_inplace(bounds):
    """
    Convert from (center, width) to (start, end)
    CAVEAT: Inplace modification!
    """

    bounds_center = np.copy(bounds[..., 0])
    bounds_size_half = np.multiply(0.5, bounds[..., 1], out=bounds[..., 1])

    np.subtract(bounds_center, bounds_size_half, out=bounds[..., 0])
    np.add(bounds_center, bounds_size_half, out=bounds[..., 1])

    return bounds


def _convert_array_cw_to_sw(bounds):
    """
    Convert from (center, width) to (start, width)
    """

    bounds_new = np.empty(bounds.shape)

    width_half = np.divide(bounds[..., 1], 2)

    bounds_new[..., 0] = np.subtract(bounds[..., 0], width_half, out=bounds_new[..., 0])
    bounds_new[..., 1] = bounds[..., 1]

    return bounds_new


def _convert_array_cw_to_sw_inplace(bounds):
    """
    Convert from (center, width) to (start, width)
    CAVEAT: Inplace modification!
    """

    width_half = np.divide(bounds[..., 1], 2)

    np.subtract(bounds[..., 0], width_half, out=bounds[..., 0])

    return bounds


def _convert_array_sw_to_se(bounds):
    """
    Convert from (start, width) to (start, end)
    """
    return _convert_array_sw_to_se_inplace(np.copy(bounds))


def _convert_array_sw_to_se_inplace(bounds):
    """
    Convert from (start, width) to (start, end)
    CAVEAT: Inplace modification!
    """
    bounds[..., 1] = np.add(bounds[..., 0], bounds[..., 1], out=bounds[..., 1])
    return bounds
