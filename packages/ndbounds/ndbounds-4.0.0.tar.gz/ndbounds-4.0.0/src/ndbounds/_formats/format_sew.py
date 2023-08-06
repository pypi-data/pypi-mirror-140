# Copyright (C) 2021 Matthias Nadig

import numpy as np

from .. import _conversion as conversion
from .. import _utils as utils

from .base import BoundFormatHandler


class NdBoundsSEW(BoundFormatHandler):
    """ Handler containing: start, end, width """

    def __init__(self, start, end, width):
        super().__init__(n_dims=start.shape[-1], shape=start.shape[:-1])
        self._start = start
        self._end = end
        self._width = width

    def _require_se(self):
        return self

    def _require_cw(self):
        center, width = conversion._convert_se_to_cw(self._start, self._end, inplace=False)
        return self._pack_secw(start=self._start, end=self._end, center=center, width=width)

    def _require_sw(self):
        return self

    def _require_secw(self):
        center, width = conversion._convert_se_to_cw(self._start, self._end, inplace=False)
        return self._pack_secw(start=self._start, end=self._end, center=center, width=width)

    def _require_start(self):
        return self

    def _require_end(self):
        return self

    def _require_center(self):
        center, width = conversion._convert_se_to_cw(self._start, self._end, inplace=False)
        return self._pack_secw(start=self._start, end=self._end, center=center, width=width)

    def _require_width(self):
        return self

    def _convert_to_se(self, inplace=False):
        return self._pack_se(start=self._start, end=self._end)

    def _convert_to_cw(self, inplace=False):
        center, width = conversion._convert_sw_to_cw(self._start, self._width, inplace=inplace)
        return self._pack_cw(center=center, width=width)

    def _convert_to_sw(self, inplace=False):
        return self._pack_sw(start=self._start, width=self._width)

    def _get_bounds_se(self, copy=True):
        return np.stack([self._start, self._end], axis=-1)

    def _get_bounds_cw(self, copy=True):
        self._raise_not_possible_for_child()

    def _get_bounds_sw(self, copy=True):
        return np.stack([self._start, self._width], axis=-1)

    def _get_start(self, copy=True):
        return utils._copy_if_required(self._start, copy=copy)

    def _get_end(self, copy=True):
        return utils._copy_if_required(self._end, copy=copy)

    def _get_center(self, copy=True):
        self._raise_not_possible_for_child()

    def _get_width(self, copy=True):
        return utils._copy_if_required(self._width, copy=copy)

    def _shift_center(self, offset_each_dim):
        center = np.subtract(self._end, self._start)
        np.add(center, offset_each_dim, out=center)
        return self._pack_cw(center=center, width=self._width)

    def _scale_dimensions(self, factor_each_dim):
        np.multiply(self._start, factor_each_dim, out=self._start)
        np.multiply(self._width, factor_each_dim, out=self._width)
        return self._pack_sw(start=self._start, width=self._width)

    def _scale_width(self, factor_each_dim):
        center = np.add(self._start, np.divide(self._width, 2))
        np.multiply(self._width, factor_each_dim, out=self._width)
        return self._pack_cw(center=center, width=self._width)

    def _apply_func_on_position(self, fn):
        center = np.add(self._start, np.divide(self._width, 2))
        fn(center, out=center)
        return self._pack_cw(center=center, width=self._width)

    def _apply_func_on_width(self, fn):
        center = np.add(self._start, np.divide(self._width, 2))
        fn(self._width, out=self._width)
        return self._pack_cw(center=center, width=self._width)

    def _copy(self):
        return self._pack_sew(start=np.copy(self._start), end=np.copy(self._end), width=np.copy(self._width))

    def _delete(self, indices, axis=None):
        if axis is None:
            start = utils._flatten_component(self._start)
            end = utils._flatten_component(self._end)
            width = utils._flatten_component(self._width)
            axis = 0
        elif axis > len(self.get_shape()):
            raise ValueError('Cannot delete elements along axis {} for bounds of shape {}'.format(
                axis, self.get_shape()))
        else:
            start = self._start
            end = self._end
            width = self._width
        start = np.delete(start, indices, axis=axis)
        end = np.delete(end, indices, axis=axis)
        width = np.delete(width, indices, axis=axis)

        return self._pack_sew(start=start, end=end, width=width)

    def _getitem(self, key):
        start = self._start[key]
        end = self._end[key]
        width = self._width[key]
        return self._pack_sew(start=start, end=end, width=width)
