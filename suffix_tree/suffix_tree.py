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


class Node:
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""
    def __init__(self, incoming_edge_start_offset, incoming_edge_end_offset, children, suffix_link=None):
        self.incoming_edge_start_offset = incoming_edge_start_offset
        self.incoming_edge_end_offset = incoming_edge_end_offset
        self.children = children
        self.suffix_link = suffix_link

    def is_root(self):
        return self.incoming_edge_start_offset == Node.UNDEFINED_OFFSET and \
               self.incoming_edge_end_offset == Node.UNDEFINED_OFFSET and \
               self.suffix_link == self

    def is_internal(self):
        return self.incoming_edge_start_offset >= 0 and \
               self.incoming_edge_end_offset >= 0 and \
               len(self.children) > 0

    def is_leaf(self):
        return len(self.children) == 0 and \
               self.incoming_edge_start_offset >= 0 and \
               self.incoming_edge_end_offset == Node.UNDEFINED_OFFSET

    @property
    def incoming_edge_length(self):
        return self.incoming_edge_end_offset - self.incoming_edge_start_offset + 1


class RootNode(Node):
    def __init__(self):
        super().__init__(-1, -1, {}, self)


class LeafNode(Node):
    def __init__(self, incoming_edge_start_offset, suffix_offset):
        super().__init__(incoming_edge_start_offset, -1, {})
        self.suffix_offset = suffix_offset


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


class Location:
    """A location is a specific value offset within a sequence.

    This could be a Node's value_offset, or it could be an offset
    in a Node's incoming edge."""
    def __init__(self, node):
        self.node = node
        self.data_source_value_offset = -1
        self.node_needing_suffix_link = None

    @property
    def data_source_value_offset(self):
        return self._data_source_value_offset

    def update_node_needing_suffix_link(self, new_node):
        if self.node_needing_suffix_link != None:
            self.node_needing_suffix_link.suffix_link = new_node
        self.node_needing_suffix_link = new_node

    def set_suffix_link(self):
        if self.node_needing_suffix_link != None and self.on_node:
            self.node_needing_suffix_link.suffix_link = self.node
            self.node_needing_suffix_link = None

    @data_source_value_offset.setter
    def data_source_value_offset(self, data_source_value_offset):
        self.on_node = (self.node.incoming_edge_end_offset == data_source_value_offset)
        self._data_source_value_offset = data_source_value_offset

    def __repr__(self):
        if self.on_node:
            return "location: {!r}".format(self.node)
        else:
            return "location: {!r}[{}]".format(self.node, self.data_source_value_offset)

class NodeFactory:
    def __init__(self):
        self.suffix_offset = 0

    def add_leaf(self, node, value, offset):
        leaf = LeafNode(offset, self.suffix_offset)
        self.suffix_offset += 1
        self.add_child(node, value, leaf)
        return leaf

    def add_child(self, node, value, child):
        node.children[value] = child
        child.parent = node

    def split_edge(self, value, node, value2, end_offset):
        new_node = Node(node.incoming_edge_start_offset, end_offset, {}, None)
        node.incoming_edge_start_offset = end_offset + 1
        self.add_child(node.parent, value, new_node)
        self.add_child(new_node, value2, node)
        return new_node

    def new_root(self):
        return RootNode()

class NodeFactoryWithId(NodeFactory):
    def __init__(self):
        self.node_id = 0
        self.suffix_offset = 0

    def next_node_id(self):
        result = self.node_id
        self.node_id += 1
        return result

    def add_leaf(self, node, value, offset):
        leaf = super().add_leaf(node, value, offset)
        leaf.node_id = self.next_node_id()

    def split_edge(self, value, node, value2, end_offset):
        new_node = super().split_edge(value, node, value2, end_offset)
        new_node.node_id = self.next_node_id()
        return new_node

    def new_root(self):
        result = super().new_root()
        result.node_id = self.next_node_id()
        return result

class TreeBuilder:
    def __init__(self, data_generator, node_factory, terminal_value=-1):
        self.data_generator = data_generator
        self.node_factory = node_factory
        self.terminal_value = terminal_value
        self.next_offset = 0
        self.data_store = DataStore()
        self.root = node_factory.new_root()
        self.location = Location(self.root)

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
                self.node_factory.add_leaf(self.location.node, value, offset)
                result = self.traverse_to_next_suffix()
                return result
        elif value == self.data_store.value_at(self.location.data_source_value_offset + 1):
            self.location.data_source_value_offset += 1
            return False
        else:
            self.location.node = self.node_factory.split_edge(
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