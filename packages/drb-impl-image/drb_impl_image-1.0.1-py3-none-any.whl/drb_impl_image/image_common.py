import enum
from typing import List, Any, Dict, Tuple, Optional

from drb import DrbNode, AbstractNode
from drb.exceptions import DrbException, DrbNotImplementationException
from drb.path import ParsedPath


class DrbImageNodesValueNames(enum.Enum):
    IMAGE = 'image'
    TAGS = 'tags'
    FORMAT = 'FormatName'
    WIDTH = 'width'
    HEIGHT = 'height'
    NUM_BANDS = 'NumBands'
    TYPE = 'Type'
    BOUNDARIES = 'Boundaries'
    CRS = 'crs'
    META = 'meta'


class DrbImageSimpleValueNode(AbstractNode):

    def __init__(self, parent: DrbNode, name: str, value: any):
        super().__init__()
        self._name = name
        self._value = value
        self._parent: DrbNode = parent
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
        return self._name

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return self._value

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException(f'No attribute {name} found')

    @property
    def children(self) -> List[DrbNode]:
        return []

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbNotImplementationException(f'no {impl} '
                                            f'implementation found')

    def close(self) -> None:
        pass
