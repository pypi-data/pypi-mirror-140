# Copyright (C) 2021 Matthias Nadig

import numpy as np

from .. import _conversion as conversion
from .. import _utils as utils

from .base import BoundFormatHandler


class NdBoundsCW(BoundFormatHandler):
    """ Handler containing: center, width """

    def __init__(self, center, width):
        super().__init__(n_dims=center.shape[-1], shape=center.shape[:-1])
        self._center = center
        self._width = width

    def _copy(self):
        return self._pack_cw(center=np.copy(self._center), width=np.copy(self._width))

    def _require_cw(self):
        return self

    def _require_se(self):
        start, end = conversion._convert_cw_to_se(self._center, self._width, inplace=False)
        return self._pack_secw(start=start, end=end, center=self._center, width=self._width)

    def _require_sw(self):
        start = np.subtract(self._center, np.divide(self._width, 2))
        return self._pack_scw(start=start, center=self._center, width=self._width)

    def _require_secw(self):
        start, end = conversion._convert_cw_to_se(self._center, self._width, inplace=False)
        return self._pack_secw(start=start, end=end, center=self._center, width=self._width)

    def _require_start(self):
        start = np.subtract(self._center, np.divide(self._width, 2))
        return self._pack_scw(start=start, center=self._center, width=self._width)

    def _require_end(self):
        end = np.add(self._center, np.divide(self._width, 2))
        return self._pack_ecw(end=end, center=self._center, width=self._width)

    def _require_center(self):
        return self

    def _require_width(self):
        return self

    def _convert_to_se(self, inplace=False):
        start, end = conversion._convert_cw_to_se(self._center, self._width, inplace=inplace)
        return self._pack_se(start=start, end=end)

    def _convert_to_cw(self, inplace=False):
        return self

    def _convert_to_sw(self, inplace=False):
        start, width = conversion._convert_cw_to_sw(self._center, self._width, inplace=inplace)
        return self._pack_sw(start=start, width=width)

    def _get_bounds_se(self, copy=True):
        self._raise_not_possible_for_child()

    def _get_bounds_cw(self, copy=True):
        return np.stack([self._center, self._width], axis=-1)

    def _get_bounds_sw(self, copy=True):
        self._raise_not_possible_for_child()

    def _get_start(self, copy=True):
        self._raise_not_possible_for_child()

    def _get_end(self, copy=True):
        self._raise_not_possible_for_child()

    def _get_center(self, copy=True):
        return utils._copy_if_required(self._center, copy=copy)

    def _get_width(self, copy=True):
        return utils._copy_if_required(self._width, copy=copy)

    def _shift_center(self, offset_each_dim):
        self._center = np.add(self._center, offset_each_dim, out=self._center)
        return self

    def _scale_dimensions(self, factor_each_dim):
        self._center = np.multiply(self._center, factor_each_dim, out=self._center)
        self._width = np.multiply(self._width, factor_each_dim, out=self._width)
        return self

    def _scale_width(self, factor_each_dim):
        self._width = np.multiply(self._width, factor_each_dim, out=self._width)
        return self

    def _delete(self, indices, axis=None):
        if axis is None:
            bounds_center = utils._flatten_component(self._center)
            bounds_width = utils._flatten_component(self._width)
            axis = 0
        elif axis > len(self.get_shape()):
            raise ValueError('Cannot delete elements along axis {} for bounds of shape {}'.format(
                axis, self.get_shape()))
        else:
            bounds_center = self._center
            bounds_width = self._width
        bounds_center = np.delete(bounds_center, indices, axis=axis)
        bounds_width = np.delete(bounds_width, indices, axis=axis)

        return self._pack_cw(center=bounds_center, width=bounds_width)

    def _getitem(self, key):
        bounds_center = self._center[key]
        bounds_width = self._width[key]
        return self._pack_cw(center=bounds_center, width=bounds_width)

    def _apply_func_on_position(self, fn):
        fn(self._center, out=self._center)
        return self

    def _apply_func_on_width(self, fn):
        fn(self._width, out=self._width)
        return self
