from suffix_tree.suffix_linker import SuffixLinker


class Modifier:
    def __init__(self, node_factory, traverser, data_store, suffix_linker):
        self.node_factory = node_factory
        self.traverser = traverser
        self.suffix_linker = suffix_linker;
        self.data_store = data_store

    def insert_value(self, location, value, offset):
        if location.on_node:
            self.node_factory.create_leaf(location.node, value, offset)
            self.location, result = self.traverser.traverse_to_next_suffix(location)
            if result and location.on_node:
                self.suffix_linker.link_to(location.node)
            return result
        else:
            location.node = self.node_factory.create_internal(
                self.data_store.value_at(location.node.incoming_edge_start_offset),
                location.node,
                self.data_store.value_at(location.data_offset + 1),
                location.data_offset)
            location.on_node = True
            return True