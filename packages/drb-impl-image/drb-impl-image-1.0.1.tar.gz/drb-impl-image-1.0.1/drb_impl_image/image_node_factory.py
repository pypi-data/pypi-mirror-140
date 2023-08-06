from typing import Any, List, Optional, Dict, Tuple

from drb import DrbNode, AbstractNode
from drb.factory import DrbFactory
from drb.path import ParsedPath

from drb_impl_image.image_node import DrbImageNode


class DrbImageBaseNode(AbstractNode):

    def __init__(self, base_node: DrbNode):
        super().__init__()

        self.base_node = base_node
        self.root_node = DrbImageNode(self)

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.base_node.parent

    @property
    def path(self) -> ParsedPath:
        return self.base_node.path

    @property
    def name(self) -> str:
        return self.base_node.name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self.base_node.namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return self.base_node.value

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return self.base_node.attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        return self.base_node.get_attribute(name, namespace_uri)

    @property
    def children(self) -> List[DrbNode]:
        return [self.root_node]

    def close(self):
        self.root_node.close()
        self.base_node.close()

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type, **kwargs) -> Any:
        return self.base_node.get_impl(impl)


class DrbImageFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        return DrbImageBaseNode(base_node=node)
