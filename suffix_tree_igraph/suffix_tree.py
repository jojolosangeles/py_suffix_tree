from itertools import count
from suffix_tree_igraph.data_store import DataStore
from suffix_tree_igraph.location import Location, LocationFactory
from suffix_tree_igraph.relocate import Relocate
from suffix_tree_igraph.suffix_tree_graph import SuffixTreeGraph


class TreeBuilder:
    def __init__(self, datasource, strategy, terminal_value=-1):
        self.offset_generator = count()
        self.data_generator = ((val,offset) for (val,offset) in zip(datasource,self.offset_generator))
        self.terminal_value = terminal_value
        self.data_store = DataStore()
        self.tree_graph = SuffixTreeGraph(strategy)
        self.relocater = Relocate(self.data_store, self.tree_graph)

    def process_all_values(self):
        """Create suffix tree from values in the data source."""
        location = Location(self.tree_graph.root)
        try:
            while True:
                location = self.process_value(location, *self.get_next_value_and_offset())
        except StopIteration:
            self.finish(location)

    def get_next_value_and_offset(self):
        value,offset = next(self.data_generator)
        self.data_store.add(value)
        self.last_offset = offset
        if (offset+1) % 100000 == 0:
            print(offset)
        return value,offset

    def finish(self, location):
        value = self.terminal_value
        return self.process_value(location, value, self.last_offset + 1)

    def process_value(self, location, value, offset):
        while True:
            location, continue_processing_value = self.process_value_at_location(location, value, offset)
            if not continue_processing_value:
                return location

    def process_value_at_location(self, location, value, offset):
        """Process the value at the given location.

        Return:
            (newLocation, True) if there is more processing to be done
            (originalLocation, False) otherwise
        """
        location, found_value = self.relocater.follow_value(location, value)
        if found_value:
            return location, False
        elif location.on_node:
            self.tree_graph.create_leaf(location.node_id, value, offset)
            location, found_value = self.relocater.go_to_suffix(location)
            if location.on_node:
                self.tree_graph.suffix_linker.link_to(location.node_id)
            return location, found_value
        else:
            incoming_edge_start_offset = location.start_offset
            internal_node = self.tree_graph.create_internal(
                self.data_store.value_at(incoming_edge_start_offset),
                location.node_id,
                self.data_store.value_at(location.data_offset + 1),
                location.data_offset)
            return LocationFactory.create_on_node(location, internal_node, incoming_edge_start_offset, location.data_offset), True
