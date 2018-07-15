from suffix_tree_igraph.data_store import DataStore
from suffix_tree_igraph.igraph_adapter import igraph_get_incoming_edge_start_offset
from suffix_tree_igraph.relocate import Relocate
from suffix_tree_igraph.location import Location, LocationFactory
from itertools import count


class TreeBuilder:
    def __init__(self, datasource, node_factory, terminal_value=-1):
        self.id_count = count()
        self.data_generator = ((val,offset) for (val,offset) in zip(datasource,self.id_count))
        self.node_factory = node_factory
        self.terminal_value = terminal_value
        self.data_store = DataStore()
        self.root_id = node_factory.create_root()
        self.relocater = Relocate(self.data_store, node_factory)

    def process_all_values(self):
        """Create suffix tree from values in the data source."""
        location = Location(self.root_id, Location.ON_NODE)
        try:
            while True:
                location = self.process_value(location, *self.get_next_value_and_offset())
        except StopIteration:
            self.finish(location)

    def number_nodes(self):
        return self.node_factory.final_id()

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
            self.node_factory.create_leaf(location.node_id, value, offset)
            location, found_value = self.relocater.go_to_suffix(location, self.node_factory)
            if location.on_node:
                self.node_factory.suffix_linker.link_to(location.node_id)
            return location, found_value
        else:
            incoming_edge_start_offset = igraph_get_incoming_edge_start_offset(location.node_id)
            location = LocationFactory.create_on_node(
                location,
                self.node_factory.create_internal(
                    self.data_store.value_at(incoming_edge_start_offset),
                    location.node_id,
                    self.data_store.value_at(location.data_offset + 1),
                    location.data_offset))
            return location, True
