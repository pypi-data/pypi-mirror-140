# Copyright (C) 2021 Matthias Nadig

import numpy as np

from .. import _conversion as conversion
from .. import _utils as utils

from .base import BoundFormatHandler


class NdBoundsECW(BoundFormatHandler):
    """ Handler containing: end, center, width """

    def __init__(self, end, center, width):
        super().__init__(n_dims=end.shape[-1], shape=end.shape[:-1])
        self._end = end
        self._center = center
        self._width = width

    def _require_se(self):
        start = np.subtract(self._end, self._width)
        return self._pack_secw(start=start, end=self._end, center=self._center, width=self._width)

    def _require_cw(self):
        return self

    def _require_sw(self):
        start = np.subtract(self._end, self._width)
        return self._pack_secw(start=start, end=self._end, center=self._center, width=self._width)

    def _require_secw(self):
        start = np.subtract(self._end, self._width)
        return self._pack_secw(start=start, end=self._end, center=self._center, width=self._width)

    def _require_start(self):
        start = np.subtract(self._end, self._width)
        return self._pack_secw(start=start, end=self._end, center=self._center, width=self._width)

    def _require_end(self):
        return self

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
        return utils._copy_if_required(self._end, copy=copy)

    def _get_center(self, copy=True):
        return utils._copy_if_required(self._center, copy=copy)

    def _get_width(self, copy=True):
        return utils._copy_if_required(self._width, copy=copy)

    def _shift_center(self, offset_each_dim):
        np.add(self._center, offset_each_dim, out=self._center)
        return self._pack_cw(center=self._center, width=self._width)

    def _scale_dimensions(self, factor_each_dim):
        np.multiply(self._center, factor_each_dim, out=self._center)
        np.multiply(self._width, factor_each_dim, out=self._width)
        return self._pack_cw(center=self._center, width=self._width)

    def _scale_width(self, factor_each_dim):
        np.multiply(self._width, factor_each_dim, out=self._width)
        return self._pack_cw(center=self._center, width=self._width)

    def _apply_func_on_position(self, fn):
        fn(self._center, out=self._center)
        return self._pack_cw(center=self._center, width=self._width)

    def _apply_func_on_width(self, fn):
        fn(self._width, out=self._width)
        return self._pack_cw(center=self._center, width=self._width)

    def _copy(self):
        return self._pack_ecw(end=np.copy(self._end), center=np.copy(self._center), width=np.copy(self._width))

    def _delete(self, indices, axis=None):
        if axis is None:
            end = utils._flatten_component(self._end)
            center = utils._flatten_component(self._center)
            width = utils._flatten_component(self._width)
            axis = 0
        elif axis > len(self.get_shape()):
            raise ValueError('Cannot delete elements along axis {} for bounds of shape {}'.format(
                axis, self.get_shape()))
        else:
            end = self._end
            center = self._center
            width = self._width
        end = np.delete(end, indices, axis=axis)
        center = np.delete(center, indices, axis=axis)
        width = np.delete(width, indices, axis=axis)

        return self._pack_ecw(end=end, center=center, width=width)

    def _getitem(self, key):
        end = self._end[key]
        center = self._center[key]
        width = self._width[key]
        return self._pack_ecw(end=end, center=center, width=width)
