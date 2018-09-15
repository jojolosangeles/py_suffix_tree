"""Node within a suffix tree."""
incoming_edge_start_offsets = []
incoming_edge_lengths = []
node_suffix_link = []
parent_node_ids = []
node_by_id = []
suffix_offsets = []

def save_node(id, node):
    node_guarantee(id)
    node_by_id[id] = node

def node_guarantee(offset):
    missing = offset - len(parent_node_ids) + 1
    while missing > 0:
        parent_node_ids.append(0)
        node_by_id.append(0)
        node_suffix_link.append(-1)
        suffix_offsets.append(-1)
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

class SingleLeaf:
    def __init__(self):
        self.id = 0
        self.suffix_offset = 0

    def is_leaf(self):
        return True

singleLeaf = SingleLeaf()

class Node:
    """Node represents an offset in a sequence of values."""
    ROOT_NODE_ID = 0

    @classmethod
    def incoming_edge_start_offset(cls, id):
        return incoming_edge_start_offsets[id]

    @classmethod
    def incoming_edge_length(cls, id):
        return incoming_edge_lengths[id]

    @classmethod
    def get(cls, id):
        global singleLeaf
        if Node.is_leaf_id(id):
            singleLeaf.id = id
            singleLeaf.suffix_offset = suffix_offsets[id]
            return singleLeaf
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
    def save_new_leaf_info(cls, node_id, parent_node_id, suffix_offset):
        node_guarantee(node_id)
        parent_node_ids[node_id] = parent_node_id
        suffix_offsets[parent_node_id] = -1
        suffix_offsets[node_id] = suffix_offset

    @classmethod
    def save_parent(cls, node_id, parent_node_id):
        parent_node_ids[node_id] = parent_node_id

    @classmethod
    def is_leaf_id(cls, node_id):
        return suffix_offsets[node_id] >= 0

    @classmethod
    def suffix(cls, node_id):
        return suffix_offsets[node_id]

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
        if parent.id == Node.ROOT_NODE_ID:
            amount_to_traverse -= 1
            value_offset += 1
        return parent.suffix_link, value_offset, amount_to_traverse

    def is_internal(self):
        return True


class SuffixLinker:

    def __init__(self):
        self.node_missing_suffix_link = None

    def needs_suffix_link(self, node):
        """Any newly created internal node needs a suffix link.  If a previously
        created node is missing its suffix link, then it just points
        to this node."""
        self.link_to(node)
        self.node_missing_suffix_link = node

    def link_to(self, node):
        if self.node_missing_suffix_link != None:
            self.node_missing_suffix_link.suffix_link = node
        self.node_missing_suffix_link = None

class RootNode(NodeWithChildren):
    def __init__(self, id):
        super().__init__(id)
        self.suffix_link = self
        node_suffix_link[0] = 0


