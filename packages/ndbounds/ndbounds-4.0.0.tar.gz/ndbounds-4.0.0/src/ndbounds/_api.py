# Copyright (C) 2021 Matthias Nadig

import numpy as np

from ._bounds import NdBounds
from . import _formats as formats
from . import _iou


def as_bounds(start=None, end=None, center=None, width=None,
              n_dims=None, copy=True, assert_order=True):
    """
    Assembles NdBounds object.
    """
    if not (start is None or end is None or center is None or width is None):
        # SECW
        raise NotImplementedError()
    elif not (start is None or end is None) and center is None and width is None:
        # SE
        bounds = _assemble_from_start_end(start, end, copy=copy, n_dims=n_dims, assert_order=assert_order)
    elif start is None and end is None and not (center is None or width is None):
        # CW
        bounds = _assemble_from_center_width(center, width, copy=copy, n_dims=n_dims)
    elif not start is None and end is None and center is None and not width is None:
        # SW
        bounds = _assemble_from_start_width(start, width, copy=copy, n_dims=n_dims)
    elif not start is None and not end is None and center is None and not width is None:
        # SEW
        _raise_invalid_combination_of_inputs(start, end, center, width)
    elif not start is None and not end is None and not center is None and width is None:
        # SEC
        _raise_invalid_combination_of_inputs(start, end, center, width)
    elif not start is None and end is None and not center is None and not width is None:
        # SCW
        _raise_invalid_combination_of_inputs(start, end, center, width)
    elif start is None and not end is None and not center is None and not width is None:
        # ECW
        _raise_invalid_combination_of_inputs(start, end, center, width)
    else:
        _raise_invalid_combination_of_inputs(start, end, center, width)

    return bounds


def interpret_as_s1s2e1e2(bounds, n_dims=2, copy=True, assert_order=True):
    """
    Assembles NdBounds object from an array, which contains a common bounding box format.
    Shape must be (..., n_dims * 2).
    The dimensions are arbitrary. Per default, 2D is assumed for more explicitness.

    Basic format is:
        [start dim 1, start dim 2, ..., start dim n, end dim 1, end dim 2, ..., end dim n]
    """
    bounds = _assert_array(bounds, copy=copy)
    if n_dims is None:
        n_dims = bounds.shape[-1] // 2
    else:
        if not bounds.shape[-1] == n_dims * 2:
            raise ValueError('Shape must be (..., n_dims * 2) for {}D, got {}'.format(n_dims, bounds.shape))
    shape_bounds = bounds.shape[:-1]
    bounds = np.swapaxes(np.reshape(bounds, shape_bounds+(2, n_dims)), -2, -1)
    return _interpret_as_se(bounds, n_dims=None, copy=False, assert_order=assert_order)


def interpret_as_s1s2w1w2(bounds, n_dims=2, copy=True):
    """
    Assembles NdBounds object from an array, which contains a common bounding box format.
    Shape must be (..., n_dims * 2).
    The dimensions are arbitrary. Per default, 2D is assumed for more explicitness.

    Basic format is:
        [start dim 1, start dim 2, ..., start dim n, width dim 1, width dim 2, ..., width dim n]
    """
    bounds = _assert_array(bounds, copy=copy)
    if not bounds.shape[-1] == n_dims * 2:
        raise ValueError('Shape must be (..., n_dims * 2) for {}D, got {}'.format(n_dims, bounds.shape))
    shape_bounds = bounds.shape[:-1]
    bounds = np.swapaxes(np.reshape(bounds, shape_bounds+(2, n_dims)), -2, -1)
    return _assemble_from_start_width(bounds[..., 0], bounds[..., 1],
                                      n_dims=None, copy=False)


def interpret_as_se(bounds, n_dims=None, copy=True, assert_order=True):
    """
    Assembles NdBounds object from an array.
    Shape must be (..., n_dims, 2).
    Along the last axis, the array contains (start, end).

    Basic format is:
        [[start dim 1, end dim 1],
         [start dim 2, end dim 2],
         ...,
         [start dim n, end dim n]]
    """
    return _interpret_as_se(bounds, n_dims=n_dims, copy=copy, assert_order=assert_order)


def interpret_as_cw(bounds, n_dims=None, copy=True):
    """
    Assembles NdBounds object from an array.
    Shape must be (..., n_dims, 2).
    Along the last axis, the array contains (center, width).

    Basic format is:
        [[center dim 1, width dim 1],
         [center dim 2, width dim 2],
         ...,
         [center dim n, width dim n]]
    """
    return _interpret_as_cw(bounds, copy=copy, n_dims=n_dims)


def iou(b1, b2):
    """
    Intersection over union (IoU) for measuring correctness of bounding boxes.
    Accepts stacks of bounds for both inputs.
    (e.g. b1 with shape (30, 2, 2) and b2 with shape (400, 15, 2, 2) result in iou with shape (30, 400, 15))
    """
    raise_if_not_ndbounds(b1)
    raise_if_not_ndbounds(b2)
    return _iou.intersection_over_union(b1, b2)


def raise_if_not_ndbounds(bounds):
    """
    Helper, that asserts that input is an NdBounds object.
    """
    if not isinstance(bounds, NdBounds):
        raise TypeError('Expected input of type \'NdBounds\', instead got \'{}\''.format(type(bounds)))


def _assert_array(bounds, copy):
    if isinstance(bounds, (np.ndarray, list, tuple)):
        if copy:
            bounds = np.copy(bounds).astype(np.float)
        else:
            bounds = np.asarray(bounds, dtype=np.float)
    else:
        raise ValueError('Unexpected type of bounds array: {}'.format(bounds))

    return bounds


def _assert_shape_of_pair(bounds):
    # Assert bounds array to be of shape (..., n_dims, 2)
    if bounds.ndim < 3 or bounds.shape[-1] != 2:
        raise ValueError('Bounds array has bad shape: (..., n_dims, 2) != {}'.format(bounds.shape))


def _assert_shape_of_individuals(arr1, arr2):
    # Assert bounds arrays to be of same shape (..., n_dims)
    if arr1.ndim < 2 or arr1.shape != arr2.shape:
        raise ValueError('Bounds arrays must be of same shape (..., n_dims, 2), got {} and {} instead'.format(
            arr1.shape, arr2.shape))


def _assert_dimensionality_pair(bounds, n_dims=None):
    # Assert n_dims to be of certain value (dimensionality of bounds themselves, not the bounds array)
    if n_dims is not None:
        if bounds.shape[-2] != n_dims:
            raise ValueError(
                'Given bounds do not fulfil user requirements. ' +
                'Requested {}-dimensional bounds, got n_dims = {}'.format(n_dims, bounds.shape[-2]))


def _assert_dimensionality_individuals(*arrays, n_dims=None):
    # Assert n_dims to be of certain value (dimensionality of bounds themselves, not the bounds array)
    if n_dims is not None:
        n_arrays = len(arrays)
        n_dims_per_array = np.empty(n_arrays, dtype=np.int)
        for i in range(n_arrays):
            n_dims_per_array[i] = arrays[i].shape[-1]
        if (n_dims_per_array != n_dims).any():
            raise ValueError(
                'Given bounds do not fulfil user requirements. ' +
                'Requested {}-dimensional bounds, got n_dims = {}'.format(n_dims, tuple(n_dims_per_array)))


def _assert_order_pair(bounds):
    _assert_order_single(bounds[..., 0], bounds[..., 1])


def _assert_order_single(bounds_start, bounds_end):
    # Check order of start and end (only in case bounds of type start-end are required)
    is_wrong_order = np.less(np.subtract(bounds_end, bounds_start), 0)
    if is_wrong_order.any():
        str_count = '{} of {} bound(s)'.format(np.sum(is_wrong_order), is_wrong_order.size)
        raise ValueError('Bounds have wrong order: start > end for {}'.format(str_count))


def _interpret_as_se(bounds, n_dims=None, copy=True, assert_order=True):
    bounds = _assert_array(bounds, copy=copy)
    _assert_shape_of_pair(bounds)
    _assert_dimensionality_pair(bounds, n_dims=n_dims)
    if assert_order:
        _assert_order_pair(bounds)
    return NdBounds(formats.NdBoundsSE(start=bounds[..., 0], end=bounds[..., 1]))


def _assemble_from_start_end(start, end, n_dims=None, copy=True, assert_order=True):
    start = _assert_array(start, copy=copy)
    end = _assert_array(end, copy=copy)
    _assert_shape_of_individuals(start, end)
    _assert_dimensionality_individuals((start, end), n_dims=n_dims)
    if assert_order:
        _assert_order_single(start, end)
    return NdBounds(formats.NdBoundsSE(start=start, end=end))


def _interpret_as_cw(bounds, n_dims=None, copy=True):
    bounds = _assert_array(bounds, copy=copy)
    _assert_shape_of_pair(bounds)
    _assert_dimensionality_pair(bounds, n_dims=n_dims)
    return NdBounds(formats.NdBoundsCW(center=bounds[..., 0], width=bounds[..., 1]))


def _assemble_from_center_width(center, width, n_dims=None, copy=True):
    center = _assert_array(center, copy=copy)
    width = _assert_array(width, copy=copy)
    _assert_shape_of_individuals(center, width)
    _assert_dimensionality_individuals((center, width), n_dims=n_dims)
    return NdBounds(formats.NdBoundsCW(center=center, width=width))


def _assemble_from_start_width(start, width, n_dims=None, copy=True):
    start = _assert_array(start, copy=copy)
    width = _assert_array(width, copy=copy)
    _assert_shape_of_individuals(start, width)
    _assert_dimensionality_individuals((start, width), n_dims=n_dims)
    return NdBounds(formats.NdBoundsSW(start=start, width=width))


def _raise_invalid_combination_of_inputs(start, end, center, width):
    raise ValueError(
        'Combination of inputs bad or not supported:' +
        ('\n\t- {}' * 4).format(
            'start  is {}None'.format('' if start is None else 'not '),
            'end    is {}None'.format('' if end is None else 'not '),
            'center is {}None'.format('' if center is None else 'not '),
            'width  is {}None'.format('' if width is None else 'not '),
        ))
