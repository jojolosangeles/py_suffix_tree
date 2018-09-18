
class DataStore:
    """Stores values processed, provides access to previously processed values"""
    def __init__(self):
        self.values = []

    def data_len(self):
        return len(self.values)

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

    def tree_str(self, node):
        return_strings = [node.__repr__()]
        return self.indent(return_strings, node.children, "  ")

    def suffix_link_str(self, node):
        if node.suffix_link == None:
            return "=> needs suffix link"
        else:
            return "=> n{}".format(node.suffix_link.id)

    def node_str(self, node):
        if node.is_leaf():
            return "({}) Leaf.{} {}, suffix_offset {}".format(
                node.id,
                node.incoming_edge_start_offset,
                self.data_store.value_str(node.incoming_edge_start_offset, node.incoming_edge_end_offset),
                node.suffix_offset)
        elif node.is_root():
            return "({}) Root".format(node.id)
        else:
            return "({}) Internal.{}.{} {} {}".format(node.id, node.incoming_edge_start_offset,
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

