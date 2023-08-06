import io
from typing import Any, List, Dict, Tuple, Optional

import drb
import numpy
import rasterio as rasterio
import xarray

from drb import DrbNode, AbstractNode
from drb.exceptions import DrbNotImplementationException, DrbException
from drb.path import ParsedPath

from drb_impl_image.execptions import DrbImageNodeException
from drb_impl_image.image_list_node import DrbImageListNode
from drb_impl_image.image_common import DrbImageNodesValueNames, \
    DrbImageSimpleValueNode
from rasterio.io import MemoryFile


class DrbImageNode(AbstractNode):

    def _get_rasterio_impl(self):
        return self._get_data_set()

    def _get_numpy_ndarray_impl(self):
        return self._get_data_set().read()

    def get_xarray_impl(self):
        return self._get_data_xarray()

    supported_impl = {
        rasterio.DatasetReader: _get_rasterio_impl,
        numpy.ndarray: _get_numpy_ndarray_impl,
        xarray.DataArray: get_xarray_impl
    }

    def __init__(self, parent: DrbNode):
        super().__init__()

        self._data_set = None
        self._data_set_file_source = None
        self._data_xarray = None
        self._parent: DrbNode = parent
        self._children: List[DrbNode] = None
        self._path = None

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def path(self) -> ParsedPath:
        if self._path is None:
            self._path = self.parent.path / self.name
        return self._path

    @property
    def name(self) -> str:
        return DrbImageNodesValueNames.IMAGE.value

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return None

    def _get_file_impl(self):
        if self._data_set_file_source is None:
            if self.parent.base_node.has_impl(io.BufferedIOBase):
                self._data_set_file_source = self.parent.base_node \
                    .get_impl(io.BufferedIOBase)
            elif self.parent.base_node.has_impl(io.BytesIO):
                self._data_set_file_source = self.parent.base_node \
                    .get_impl(io.BytesIO)
            else:
                raise DrbImageNodeException(f'Unsupported parent '
                                            f'{type(self.parent).__name__} '
                                            f'for DrbImageNode')

    def _get_data_set(self) -> rasterio.DatasetReader:
        if self._data_set is None:
            self._get_file_impl()
            self._memory_file = MemoryFile(
                file_or_bytes=self._data_set_file_source)
            self._data_set = self._memory_file.open()

        return self._data_set

    def _get_data_xarray(self) -> rasterio.DatasetReader:
        if self._data_xarray is None:
            self._get_data_set()
            self._data_xarray = xarray.open_rasterio(
                self._data_set)
        return self._data_xarray

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException(f'Attribute not found name: {name}, '
                           f'namespace: {namespace_uri}')

    def _add_node_value(self, node_name, value):
        node_value = DrbImageSimpleValueNode(self, node_name, value)
        self._children.append(node_value)

    def _add_node_value_from_dict(self, node_name, dictionary, key):
        if key in dictionary:
            value = dictionary[key]
        else:
            value = None
        self._add_node_value(node_name, value)

    def _add_values_from_dict(self, list_name, dictionary):

        list_node = DrbImageListNode(self, list_name)
        for node_name, value in dictionary.items():
            node_value = DrbImageSimpleValueNode(list_node, node_name, value)
            list_node.append_child(node_value)

        self._children.append(list_node)

    @property
    @drb.resolve_children
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            data_set = self._get_data_set()

            self._add_node_value_from_dict(DrbImageNodesValueNames.FORMAT
                                           .value, data_set.meta, 'driver')

            self._add_node_value(DrbImageNodesValueNames.WIDTH.value,
                                 data_set.width)
            self._add_node_value(DrbImageNodesValueNames.HEIGHT.value,
                                 data_set.height)
            self._add_node_value(DrbImageNodesValueNames.NUM_BANDS.value,
                                 data_set.count)
            self._add_node_value_from_dict(DrbImageNodesValueNames.TYPE.value,
                                           data_set.meta, 'dtype')
            self._add_node_value_from_dict(DrbImageNodesValueNames.CRS.value,
                                           data_set.meta, 'crs')

            if data_set.tags() is not None:
                self._add_values_from_dict(DrbImageNodesValueNames.TAGS.value,
                                           data_set.tags())
            if data_set.tags() is not None:
                self._add_values_from_dict(DrbImageNodesValueNames.META.value,
                                           data_set.meta)
        return self._children

    def has_impl(self, impl: type) -> bool:
        if impl in self.supported_impl.keys():
            return True

    def get_impl(self, impl: type, **kwargs) -> Any:
        try:
            return self.supported_impl[impl](self)
        except KeyError:
            raise DrbNotImplementationException(
                f'no {impl} implementation found')

    def close(self):
        if self._data_set is not None:
            self._data_set.close()
        if self._data_set_file_source is not None:
            self._data_set_file_source.close()
        if self._data_xarray is not None:
            self._data_xarray.close()
