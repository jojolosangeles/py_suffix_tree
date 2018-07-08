from suffix_tree.data_store import DataStore
from suffix_tree.relocate import Relocate
from suffix_tree.location import Location, LocationFactory
from itertools import count


class TreeBuilder:
    def __init__(self, datasource, node_factory, terminal_value=-1):
        self.id_count = count()
        self.data_generator = ((val,offset) for (val,offset) in zip(datasource,self.id_count))
        self.node_factory = node_factory
        self.terminal_value = terminal_value
        self.data_store = DataStore()
        self.root = node_factory.create_root()
        self.relocater = Relocate(self.data_store)

    def process_all_values(self):
        """Create suffix tree from values in the data source."""
        location = Location(self.root, Location.ON_NODE)
        try:
            while True:
                location = self.process_value(location, *self.get_next_value_and_offset())
        except StopIteration:
            self.finish(location)

    def final_id(self):
        return next(self.id_count)

    def get_next_value_and_offset(self):
        value,offset = next(self.data_generator)
        self.data_store.add(value)
        self.last_offset = offset
        if offset % 100000 == 0:
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
            self.node_factory.create_leaf(location.node, value, offset)
            location, found_value = self.relocater.go_to_suffix(location)
            if location.on_node:
                self.node_factory.suffix_linker.link_to(location.node)
            return location, found_value
        else:
            location = LocationFactory.create(
                self.node_factory.create_internal(
                    self.data_store.value_at(location.node.incoming_edge_start_offset),
                    location.node,
                    self.data_store.value_at(location.data_offset + 1),
                    location.data_offset), Location.ON_NODE)
            return location, True
