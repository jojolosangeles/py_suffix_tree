
class DataStore:
    """Stores values as they are encountered, provides access to previous values"""
    def __init__(self):
        self.values = []

    def add(self, value):
        self.values.append(value)

    def get_values(self, start_offset, end_offset):
        return [value for value in self.values[start_offset:(end_offset+1)]]

    def value_str(self, start_offset, end_offset):
        if end_offset == -1:
            return ''.join(self.values[start_offset:])
        else:
            return ''.join(self.values[start_offset:end_offset + 1])

    def value_at(self, offset):
        try:
            return self.values[offset]
        except IndexError:
            #print("Offset={}, number values={}".format(offset, len(self.values)))
            return 0



class NodeStr:
    """Create string forms of a node or tree.

    Not using __repr__ or __str__ because this nodes only store value offsets,
    actual values are in DataStore instance"""
    def __init__(self, data_store):
        self.data_store = data_store

    def suffix_link_str(self, node):
        if node.suffix_link == None:
            return "=> needs suffix link"
        else:
            return "=> n{}".format(node.suffix_link.id)

    def edge_str(self, node):
        return self.data_store.value_str(node.incoming_edge_start_offset, node.incoming_edge_end_offset)


