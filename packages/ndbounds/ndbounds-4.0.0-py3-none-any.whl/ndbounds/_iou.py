# Copyright (C) 2021 Matthias Nadig

import numpy as np


def intersection_over_union(b1, b2):
    """ Intersection over union (IoU) """

    # Put both stacks together along a new first axis
    b1_se = b1.get_bounds_se(copy=False)
    b2_se = b2.get_bounds_se(copy=False)
    bounds_stack = _combine_bounds_to_stack(b1_se, b2_se)

    # Calculate IoU
    iou = _iou_on_stack(bounds_stack)

    # If given two single bounds (no stack), return float instead of array
    if iou.shape == ():
        iou = float(iou)

    return iou


def _combine_bounds_to_stack(bounds1, bounds2):
    shape_stack1 = bounds1.shape[:-2]
    shape_stack2 = bounds2.shape[:-2]

    # Repeat both stacks so that they have the same shape
    for n_repeat in shape_stack1:
        bounds2 = np.repeat(bounds2[np.newaxis], n_repeat, axis=0)
    for n_repeat in shape_stack2:
        bounds1 = np.repeat(bounds1[..., np.newaxis, :, :], n_repeat, axis=-3)

    # Put both stacks together along a new first axis
    bounds_stack = np.stack([bounds1, bounds2])

    return bounds_stack


def _iou_on_stack(bounds_stack):
    """ Calculate the IoU on a prepared stack (see intersection_over_union) """

    # Area (1D: range; 3D: volume) of each bounds
    areas = np.prod(np.subtract(bounds_stack[..., 1], bounds_stack[..., 0]), axis=-1)

    # Get smaller and bigger values per dimension in correct order
    bounds_start = np.min(bounds_stack, axis=-1)
    bounds_stop = np.max(bounds_stack, axis=-1)

    # Intersections between bounds along each dimension
    intersect_per_dim = np.subtract(np.min(bounds_stop, axis=0), np.max(bounds_start, axis=0))
    intersect_per_dim = np.maximum(0, intersect_per_dim)

    # Area (1D: range; 3D: volume) of intersection
    area_intersect = np.prod(intersect_per_dim, axis=-1)

    # Finally calculate IoU (and account for cases with zero-division)
    divisor = np.subtract(np.sum(areas, axis=0), area_intersect)

    # Given an array of IoUs for stack of bounds, get indices that are concerned by zero-division
    is_not_zero_division = divisor != 0

    # Division where divisor not 0, else 0 (realized by writing result into array of zeros)
    iou = np.divide(area_intersect, divisor,
                    out=np.zeros_like(area_intersect, dtype=np.float),
                    where=is_not_zero_division)

    return iou
