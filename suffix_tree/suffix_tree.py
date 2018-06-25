from suffix_tree.node import Node
from suffix_tree.tree_location import TreeLocation


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
    def __init__(self, data_generator, node_factory, terminal_value=-1):
        self.data_generator = data_generator
        self.node_factory = node_factory
        self.terminal_value = terminal_value
        self.next_offset = 0
        self.data_store = DataStore()
        self.root = node_factory.create_root()
        self.location = TreeLocation(self.root)

    def next(self):
        value = next(self.data_generator)
        offset = self.next_offset
        self.data_store.add(value)
        self.next_offset += 1
        return value,offset

    def finish(self):
        value = self.terminal_value
        offset = self.next_offset
        self.process_value(value, offset)

    def run_steps(self):
        try:
            while True:
                value,offset = self.next()
                self.runstep(value, offset)
        except StopIteration:
            pass

    def process_value(self, value, offset):
        while self.process_value_at_location(value, offset):
            pass

    def process_value_at_location(self, value, offset):
        if self.location.on_node:
            if value in self.location.node.children:
                self.location.node = self.location.node.children[value]
                self.location.data_source_value_offset = self.location.node.incoming_edge_start_offset
                return False
            else:
                self.node_factory.create_leaf(self.location.node, value, offset)
                result = self.traverse_to_next_suffix()
                return result
        elif value == self.data_store.value_at(self.location.data_source_value_offset + 1):
            self.location.data_source_value_offset += 1
            return False
        else:
            self.location.node = self.node_factory.create_internal(
                self.data_store.value_at(self.location.node.incoming_edge_start_offset),
                self.location.node,
                self.data_store.value_at(self.location.data_source_value_offset + 1),
                self.location.data_source_value_offset)
            self.location.update_node_needing_suffix_link(self.location.node)
            self.location.on_node = True
            return True
        raise ValueError

    def traverse_to_next_suffix(self):
        """
        Traverse to the suffix for this node.

        Return:
                True if the location changed, otherwise False
        """
        next_node = self.location.node.suffix_link
        if next_node == self.location.node:
            return False
        elif next_node == None:
            # we have no suffix link, traverse up
            amount_to_traverse = self.location.node.incoming_edge_length
            parent = self.location.node.parent
            value_offset = self.location.node.incoming_edge_start_offset
            # the root suffix link is to itself, so we have to manually skip first character
            if parent.suffix_link == parent:
                value_offset += 1
                amount_to_traverse -= 1
            start_node = parent.suffix_link
            self.traverse_down(start_node,
                               value_offset,
                               amount_to_traverse)
        else:
            self.location.node = next_node

        self.location.set_suffix_link()
        return True

    def traverse_down(self, node, offset, amount_to_traverse):
        if amount_to_traverse == 0:
            self.location.node = node
            self.location.data_source_value_offset = node.incoming_edge_end_offset
        else:
            self.location.node = node.children[self.data_store.value_at(offset)]
            if self.location.node.is_leaf() or self.location.node.incoming_edge_length >= amount_to_traverse:
                self.location.data_source_value_offset = self.location.node.incoming_edge_start_offset + amount_to_traverse - 1
            else:
                edge_length = self.location.node.incoming_edge_length
                amount_to_traverse -= edge_length
                return self.traverse_down(self.location.node, offset + edge_length, amount_to_traverse)

    def __repr__(self):
        return "{!r}".format(self.location)