"""Node within a suffix tree."""

class GraphEntity:
    """The GraphEntity is the replacement for the Node, and modelled after dynamoDB table design.
╔══════════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╗
║  PK      ║  SK  ║ iESO ║ iEVS ║ tNID ║ pNID ║ sO   ║ sL   ║
╠══════════╬══════╬══════╬══════╬══════╬══════╬══════╬══════╣
║  root    ║ self ║  -   ║  -   ║  -   ║  -   ║  -   ║  -   ║
║  root    ║ A    ║  -   ║  -   ║  i1  ║  -   ║  -   ║  -   ║
║  root    ║ B    ║  -   ║  -   ║  i2  ║  -   ║  -   ║  -   ║
║  root    ║ X    ║  2   ║  -   ║  -   ║ root ║  2   ║  -   ║
║  root    ║ Y    ║  3   ║  -   ║  -   ║ root ║  3   ║  -   ║
║  root    ║ C    ║  6   ║  -   ║  -   ║ root ║  6   ║  -   ║
║  root    ║ D    ║  7   ║  -   ║  -   ║ root ║  7   ║  -   ║
╠══════════╬══════╬══════╬══════╬══════╬══════╬══════╬══════╣
║   i1     ║ self ║  -   ║ AB   ║  -   ║ root ║  -   ║  i2  ║
║   i1     ║ X    ║  2   ║  -   ║  -   ║ i1   ║  0   ║  -   ║
║   i1     ║ C    ║  6   ║  -   ║  -   ║ i1   ║  4   ║  -   ║
╠══════════╬══════╬══════╬══════╬══════╬══════╬══════╬══════╣
║   i2     ║ self ║  -   ║ B    ║  -   ║ root ║  -   ║  -   ║
║   i2     ║ X    ║  2   ║  -   ║  -   ║ i2   ║  1   ║  -   ║
║   i2     ║ C    ║  6   ║  -   ║  -   ║ i2   ║  5   ║  -   ║
╚══════════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╝

For refactoring, first I will have the GraphEntity hold the data for the node
    """
    SELF = "self"

    def __init__(self, PK, SK, iESO, iEVS, tNID, pNID, sO, sL):
        self.PK = PK
        self.SK = SK
        self.iESO = iESO
        self.iEVS = iEVS
        self.tNID = tNID
        self.pNID = pNID
        self.sO = sO
        self.sL = sL

    def is_root(self):
        return self.sL == self.PK

    @staticmethod
    def getValues(start, end):
        return ""

    @staticmethod
    def factory(id, incoming_edge_start_offset, incoming_edge_end_offset, children, suffix_link):
        return GraphEntity(PK=id,
                           SK=GraphEntity.SELF,
                           iESO=incoming_edge_start_offset if incoming_edge_end_offset == Node.UNDEFINED_OFFSET else None,
                           iEVS=None if incoming_edge_end_offset == Node.UNDEFINED_OFFSET else GraphEntity.getValues(incoming_edge_start_offset, incoming_edge_end_offset),
                           tNID=None,
                           pNID=None,
                           sO=-0,
                           sL=suffix_link)

class Node:
    """Node represents a sub-sequence of values found at multiple locations in the total sequence.
    The exact locations in the total sequence are in the LeafNodes 'suffix_offset' values below
    this Node.  A LeafNode respresents only one location (the suffix_offset), and a RootNode
    represents all locations."""
    UNDEFINED_OFFSET = -1
    def __init__(self, id, incoming_edge_start_offset, incoming_edge_end_offset=UNDEFINED_OFFSET, children=None,
                 suffix_link=None):
        self.id = id
        self.incoming_edge_start_offset = incoming_edge_start_offset
        self.incoming_edge_end_offset = incoming_edge_end_offset
        self.children = children
        self.suffix_link = suffix_link
        self.graph_entity = GraphEntity.factory(id, incoming_edge_start_offset, incoming_edge_end_offset, children, suffix_link)

    # Trying to transition to "graph_entity"
    def is_root(self):
        return self.suffix_link == self

    def is_leaf(self):
        return self.children is None

    def incoming_edge_length(self):
        return self.incoming_edge_end_offset - self.incoming_edge_start_offset + 1


class RootNode(Node):
    def __init__(self, id):
        super().__init__(id, Node.UNDEFINED_OFFSET, Node.UNDEFINED_OFFSET, {}, self)

    def incoming_edge_length(self):
        return 0


class LeafNode(Node):
    def __init__(self, id, incoming_edge_start_offset, suffix_offset):
        super().__init__(id, incoming_edge_start_offset)
        self.suffix_offset = suffix_offset

    def incoming_edge_length(self):
        return 0


class NodeFlattener:
    """Writes out a node in suffix tree as text."""
    ROOT_FORMAT = "R {id}\n"
    INTERNAL_FORMAT = "I {id} {parent_id} {incoming_sequence_id} {leaf_count} {depth}\n"
    LEAF_FORMAT = "L {id} {parent_id} {incoming_sequence_id} {suffix_offset}\n"

    def __init__(self, writer):
        self.writer = writer
        self.writer.write("# {fmt}".format(fmt=self.ROOT_FORMAT))
        self.writer.write("# {fmt}".format(fmt=self.INTERNAL_FORMAT))
        self.writer.write("# {fmt}".format(fmt=self.LEAF_FORMAT))

    def write_root(self, node):
        self.writer.write(self.ROOT_FORMAT.format(id=node.id))

    def write_leaf(self, node):
        self.writer.write(self.LEAF_FORMAT.format(
            id = node.id,
            parent_id = node.parent.id,
            leaf_count = node.leaf_count,
            incoming_sequence_id = node.incoming_sequence_id,
            suffix_offset = node.suffix_offset
        ))

    def write_internal(self, node):
        self.writer.write(self.INTERNAL_FORMAT.format(
            id = node.id,
            parent_id = node.parent.id,
            leaf_count = node.leaf_count,
            depth = node.depth,
            incoming_sequence_id = node.incoming_sequence_id
        ))