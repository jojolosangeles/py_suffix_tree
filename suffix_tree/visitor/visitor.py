from collections import defaultdict
from multiprocessing import SimpleQueue

from suffix_tree.node import Node

class Visitor:
    def visit(self, node):
        pass

    def after_children_visited(self, node):
        pass

class NodeBFS:
    def __init__(self):
        self.node_queue = SimpleQueue()

    def __call__(self, visitor, node, final_suffix_offset=0):
        self.final_suffix_offset = final_suffix_offset
        self.node_queue.put(node)
        self.bfs(visitor, node)

    def bfs(self, visitor, node):
        while not self.node_queue.empty():
            node = self.node_queue.get()
            visitor.visit(node, self.final_suffix_offset)
            if node.children != None:
                for child in node.children:
                    self.node_queue.put(node.children[child])


class NodeDFS:
    def __call__(self, visitor, node, final_suffix_offset=0):
        visitor.visit(node, final_suffix_offset)
        if node.children != None:
            for child in node.children:
                self(visitor, node.children[child], final_suffix_offset)
        visitor.after_children_visited(node)

# TwoWayDict from https://stackoverflow.com/questions/1456373/two-way-reverse-map
# and https://stackoverflow.com/questions/904036/chain-calling-parent-constructors-in-python
class TwoWayDict(defaultdict):
    def __init__(self):
        super(TwoWayDict,self).__init__(lambda:None)

    def __setitem__(self, key, value):
        # Remove any previous connections with these values
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        """Returns the number of connections"""
        return dict.__len__(self) // 2


def int_generator(initial_value):
    current_value = initial_value
    while True:
        result = current_value
        current_value += 1
        yield result


class Flattener(Visitor):
    def __init__(self, data_source, data_sink, dict_sink):
        self.data_source = data_source
        self.data_sink = data_sink
        self.dict_sink = dict_sink
        self.id_seq_mapper = TwoWayDict()
        self.last_id = 0
        self.dict_id_generator = int_generator(1)

    def get_sequence_id(self, str_value):
        id = self.id_seq_mapper[str_value]
        if id == None:
            id = next(self.dict_id_generator)
            self.id_seq_mapper[id] = str_value
            self.dict_sink.write("{id} {value}\n".format(id=id,value=str_value))
        self.last_id = id
        return id

    def visit(self, node, final_suffix_offset=0):
        if node.is_root():
            self.data_sink.write_root(node)
        elif node.is_leaf():
            node.incoming_sequence_id = self.get_sequence_id(
                self.data_source.value_str(node.incoming_edge_start_offset, node.incoming_edge_end_offset))
            self.data_sink.write_leaf(node)
        else:
            node.incoming_sequence_id = self.get_sequence_id(
                self.data_source.value_str(node.incoming_edge_start_offset, node.incoming_edge_end_offset))
            self.data_sink.write_internal(node)


class SuffixCollector(Visitor):
    def __init__(self, result):
        self.suffixes = result

    def visit(self, node, final_suffix_offset=0):
        if node.is_leaf():
            self.suffixes.append(node.suffix_offset)

class PrintVisitor:
    def __init__(self):
        self.visit_depth = 0

    def visit(self, node, final_suffix_offset):
        self.visit_depth += 1
        if node.is_root():
            print("root")
        else:
            print("{}lf={}, depth={}, {}-{}".format("   "*self.visit_depth, node.leaf_count, node.depth, node.incoming_edge_start_offset, "*" if node.incoming_edge_end_offset < 0 else node.incoming_edge_end_offset))

    def after_children_visited(self, node):
        self.visit_depth -= 1


class LeafCountVisitor:
    def __init__(self, final_suffix_offset):
        self.final_suffix_offset = final_suffix_offset

    def visit(self, node, final_suffix_offset):
        if node.is_leaf():
            node.leaf_count = 1

    def after_children_visited(self, node):
        if not node.is_leaf():
            node.leaf_count = sum([node.children[child].leaf_count for child in node.children])


class DepthVisitor(Visitor):
    def visit(self, node, final_suffix_offset):
        if node.is_root():
            node.depth = 0
        elif node.is_leaf():
            node.depth = final_suffix_offset - node.incoming_edge_start_offset + node.parent.depth
        else:
            node.depth = node.incoming_edge_length() + node.parent.depth


class OffsetAdjustingVisitor(Visitor):
    def __init__(self, starting_offset):
        self.starting_offset = starting_offset

    def visit(self, node, final_suffix_offset):
        if node.incoming_edge_start_offset != Node.UNDEFINED_OFFSET:
            node.incoming_edge_start_offset += self.starting_offset
        if node.incoming_edge_end_offset != Node.UNDEFINED_OFFSET:
            node.incoming_edge_end_offset += self.starting_offset
