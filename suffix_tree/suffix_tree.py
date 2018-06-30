from suffix_tree.suffix_linker import SuffixLinker
from suffix_tree.traverser import Traverser
from suffix_tree.tree_location import TreeLocation
from itertools import count

class DataStore:
    """Stores values as they are encountered, provides access to previous values"""
    def __init__(self):
        self.values = []

    def add(self, value):
        self.values.append(value)

    def value_str(self, start_offset, end_offset):
        if end_offset == -1:
            return ''.join(self.values[start_offset:])
        else:
            return ''.join(self.values[start_offset:end_offset + 1])

    def value_at(self, offset):
        return self.values[offset]


class NodeStr:
    """Create string forms of a node or tree.

    Not using __repr__ or __str__ because this nodes only store value offsets,
    actual values are in DataStore instance"""
    def __init__(self, data_store):
        self.data_store = data_store

    def tree_str(self, node):
        return_strings = [node.__repr__()]
        return self.indent(return_strings, node.children, "  ")

    def suffix_link_str(self, node):
        if node.suffix_link == None:
            return "=> needs suffix link"
        else:
            return "=> n{}".format(node.suffix_link.node_id)

    def node_str(self, node):
        if node.is_leaf():
            return "({}) Leaf.{} {}, suffix_offset {}".format(
                node.node_id,
                node.incoming_edge_start_offset,
                self.data_store.value_str(node.incoming_edge_start_offset, node.incoming_edge_end_offset),
                node.suffix_offset)
        elif node.is_root():
            return "({}) Root".format(node.node_id)
        else:
            return "({}) Internal.{}.{} {} {}".format(node.node_id, node.incoming_edge_start_offset,
                                                      node.incoming_edge_end_offset,
                                                      self.edge_str(node),
                                                      self.suffix_link_str(node))

    def edge_str(self, node):
        return self.data_store.value_str(node.incoming_edge_start_offset, node.incoming_edge_end_offset)

    def indent(self, strings, children, prefix):
        if children != None:
            for child in children.values():
                strings.append(prefix + self.node_str(child))
                self.indent(strings, child.children, "  " + prefix)
        return "\n".join(strings)


class TreeBuilder:
    def __init__(self, datasource, node_factory, terminal_value=-1):
        self.data_generator = ((val,offset) for (val,offset) in zip(datasource,count()))
        self.node_factory = node_factory
        self.terminal_value = terminal_value
        self.data_store = DataStore()
        self.root = node_factory.create_root()
        self.location = TreeLocation(self.root)
        self.suffix_linker = SuffixLinker();
        self.traverser = Traverser(self.data_store)

    def process_all_values(self):
        """Create suffix tree from values in the data source."""
        try:
            while True:
                self.process_value(*self.get_next_value_and_offset())
        except StopIteration:
            self.finish()

    def get_next_value_and_offset(self):
        value,offset = next(self.data_generator)
        self.data_store.add(value)
        self.last_offset = offset
        return value,offset

    def finish(self):
        value = self.terminal_value
        self.process_value(value, self.last_offset + 1)

    def process_value(self, value, offset):
        while self.process_value_at_location(value, offset):
            pass

    def process_value_at_location(self, value, offset):
        """Process the value at the given location.

        Return:
            True if there is more processing to be done
            """
        self.location, result = self.traverser.traverse_by_value(self.location, value)
        if result:
            return False
        else:
            return self.insert_value(value, offset)

    def insert_value(self, value, offset):
        if self.location.on_node:
            self.node_factory.create_leaf(self.location.node, value, offset)
            self.location, result = self.traverser.traverse_to_next_suffix(self.location)
            if result and self.location.on_node:
                self.suffix_linker.link_to(self.location.node)
            return result
        else:
            self.location.node = self.node_factory.create_internal(
                self.data_store.value_at(self.location.node.incoming_edge_start_offset),
                self.location.node,
                self.data_store.value_at(self.location.data_source_value_offset + 1),
                self.location.data_source_value_offset)
            self.suffix_linker.needs_suffix_link(self.location.node)
            self.location.on_node = True
            return True

    def __repr__(self):
        return "{!r}".format(self.location)