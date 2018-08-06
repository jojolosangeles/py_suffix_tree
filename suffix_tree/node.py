"""Node within a suffix tree."""
incoming_edge_start_offsets = []
incoming_edge_lengths = []

parent_node_ids = []
node_by_id = []

def save_node(id, node):
    node_guarantee(id)
    node_by_id[id] = node

def node_guarantee(offset):
    missing = offset - len(parent_node_ids) + 1
    while missing > 0:
        parent_node_ids.append(0)
        node_by_id.append(0)
        missing -= 1

def save_node_parent(node_id, parent_node_id):
    node_guarantee(max(node_id, parent_node_id))
    parent_node_ids[node_id] = parent_node_id

def edge_guarantee(offset):
    missing = offset - len(incoming_edge_lengths) + 1
    while missing > 0:
        incoming_edge_lengths.append(0)
        incoming_edge_start_offsets.append(0)
        missing -= 1


def edge_save(id, start_offset, edge_length):
    edge_guarantee(id)
    incoming_edge_start_offsets[id] = start_offset
    incoming_edge_lengths[id] = edge_length

def edge_adjust(id, amount):
    incoming_edge_start_offsets[id] += amount
    if incoming_edge_lengths[id] > 0:
        incoming_edge_lengths[id] -= amount

class Edge:
    def __init__(self, start_offset, edge_length, adjacent_node):
        self.start_offset = start_offset
        self.edge_length = edge_length
        self.adjacent_node = adjacent_node
        if adjacent_node != None:
            edge_save(adjacent_node.id, start_offset, edge_length)

    def shrink_by(self, amount):
        self.start_offset += amount
        if self.edge_length > 0:
            self.edge_length -= amount

    def copy(self):
        return Edge(self.start_offset, self.edge_length, self.adjacent_node)

    def covers(self, length):
        return self.edge_length > length or self.edge_length < 0

class Node:
    """Node represents an offset in a sequence of values."""

    @classmethod
    def incoming_edge_start_offset(cls, id):
        return incoming_edge_start_offsets[id]

    @classmethod
    def incoming_edge_length(cls, id):
        return incoming_edge_lengths[id]

    @classmethod
    def get(cls, id):
        return node_by_id[id]

    @classmethod
    def fill(cls, node_id, edge):
        edge.start_offset = incoming_edge_start_offsets[node_id]
        edge.edge_length = incoming_edge_lengths[node_id]
        edge.adjacent_node = node_by_id[node_id]

    @classmethod
    def parent(cls, node_id):
        return node_by_id[parent_node_ids[node_id]]

    @classmethod
    def save_parent(cls, node_id, parent_node_id):
        parent_node_ids[node_id] = parent_node_id

    def __init__(self, id):
        self.id = id
        save_node(id, self)

    def is_root(self):
        return False

    def is_leaf(self):
        return False

    def is_internal(self):
        return True

class NodeWithChildren(Node):
    def __init__(self, id):
        super().__init__(id)
        self.children_ids = {}

    def has_child_value(self, value):
        return value in self.children_ids

class InternalNode(NodeWithChildren):
    UNDEFINED_OFFSET = -1

    """Node represents an offset in a sequence of values."""

    def __init__(self, id):
        super().__init__(id)
        self.suffix_link = None

    def get_suffix_traversal_info(self):
        parent = node_by_id[parent_node_ids[self.id]]
        value_offset = incoming_edge_start_offsets[self.id]
        amount_to_traverse = incoming_edge_lengths[self.id]
        if parent.is_root():
            amount_to_traverse -= 1
            value_offset += 1
        return parent.suffix_link, value_offset, amount_to_traverse

    def is_internal(self):
        return True


class RootNode(NodeWithChildren):
    def __init__(self, id):
        super().__init__(id)
        self.suffix_link = self

    def is_root(self):
        return True


class LeafNode(Node):
    def __init__(self, id, suffix_offset):
        super().__init__(id)
        self.suffix_offset = suffix_offset

    def is_leaf(self):
        return True

    def has_child_value(self, value):
        return False