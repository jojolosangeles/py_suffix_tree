from collections import defaultdict
from suffix_tree.visitor.visitor import Visitor

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
    """Write out suffix tree as text, one line per node along with a dictionary
    of all value sequences used in the tree.

    The dictionary size is limited by the data source, the MmapDataStore only
    returns MmapDataStore.MAX_READ_SIZE values."""
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

    def visit(self, node, nodeStore):
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