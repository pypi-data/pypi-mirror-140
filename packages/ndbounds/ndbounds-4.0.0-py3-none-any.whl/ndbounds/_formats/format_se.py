# Copyright (C) 2021 Matthias Nadig

import numpy as np

from .. import _conversion as conversion
from .. import _utils as utils

from .base import BoundFormatHandler


class NdBoundsSE(BoundFormatHandler):
    """ Handler containing: start, end """

    def __init__(self, start, end):
        super().__init__(n_dims=start.shape[-1], shape=start.shape[:-1])
        self._start = start
        self._end = end

    def _copy(self):
        return self._pack_se(start=np.copy(self._start), end=np.copy(self._end))

    def _require_se(self):
        return self

    def _require_cw(self):
        center, width = conversion._convert_se_to_cw(self._start, self._end, inplace=False)
        return self._pack_secw(start=self._start, end=self._end, center=center, width=width)

    def _require_sw(self):
        width = np.subtract(self._end, self._start)
        return self._pack_sew(start=self._start, end=self._end, width=width)

    def _require_secw(self):
        center, width = conversion._convert_se_to_cw(self._start, self._end, inplace=False)
        return self._pack_secw(start=self._start, end=self._end, center=center, width=width)

    def _require_start(self):
        return self

    def _require_end(self):
        return self

    def _require_center(self):
        center = np.add(self._start, self._end)
        center = np.divide(center, 2, out=center)
        return self._pack_sec(start=self._start, end=self._end, center=center)

    def _require_width(self):
        width = np.subtract(self._end, self._start)
        return self._pack_sew(start=self._start, end=self._end, width=width)

    def _convert_to_se(self, inplace=False):
        return self

    def _convert_to_cw(self, inplace=False):
        center, width = conversion._convert_se_to_cw(self._start, self._end, inplace=inplace)
        return self._pack_cw(center=center, width=width)

    def _convert_to_sw(self, inplace=False):
        start, width = conversion._convert_se_to_sw(self._start, self._end, inplace=inplace)
        return self._pack_sw(start=start, width=width)

    def _get_bounds_se(self, copy=True):
        return np.stack([self._start, self._end], axis=-1)

    def _get_bounds_cw(self, copy=True):
        self._raise_not_possible_for_child()

    def _get_bounds_sw(self, copy=True):
        self._raise_not_possible_for_child()

    def _get_start(self, copy=True):
        return utils._copy_if_required(self._start, copy=copy)

    def _get_end(self, copy=True):
        return utils._copy_if_required(self._end, copy=copy)

    def _get_center(self, copy=True):
        self._raise_not_possible_for_child()

    def _get_width(self, copy=True):
        self._raise_not_possible_for_child()

    def _shift_center(self, offset_each_dim):
        np.add(self._start, offset_each_dim, out=self._start)
        np.add(self._end, offset_each_dim, out=self._end)
        return self

    def _scale_dimensions(self, factor_each_dim):
        np.multiply(self._start, factor_each_dim, out=self._start)
        np.multiply(self._end, factor_each_dim, out=self._end)
        return self

    def _scale_width(self, factor_each_dim):
        self._raise_not_possible_for_child()

    def _delete(self, indices, axis=None):
        if axis is None:
            start = utils._flatten_component(self._start)
            end = utils._flatten_component(self._end)
            axis = 0
        elif axis > len(self.get_shape()):
            raise ValueError('Cannot delete elements along axis {} for bounds of shape {}'.format(
                axis, self.get_shape()))
        else:
            start = self._start
            end = self._end
        start = np.delete(start, indices, axis=axis)
        end = np.delete(end, indices, axis=axis)

        return self._pack_se(start=start, end=end)

    def _getitem(self, key):
        start = self._start[key]
        end = self._end[key]
        return self._pack_se(start=start, end=end)

    def _apply_func_on_position(self, fn):
        width = np.subtract(self._end, self._start)
        center = np.add(self._start, np.divide(width, 2))
        fn(center, out=center)
        return self._pack_cw(center=center, width=width)

    def _apply_func_on_width(self, fn):
        self._raise_not_possible_for_child()
