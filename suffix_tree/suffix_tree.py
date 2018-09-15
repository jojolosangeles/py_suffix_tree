from suffix_tree.data_store import DataStore
from suffix_tree.location import Location
from itertools import count

from suffix_tree.node_factory import NodeFactory
from suffix_tree.node import SuffixLinker


class TreeBuilder:
    def __init__(self, datasource, terminal_value=-1):
        self.id_count = count()
        self.data_generator = ((val,offset) for (val,offset) in zip(datasource,self.id_count))
        self.data_store = DataStore()
        self.node_factory = NodeFactory(self.data_store)
        self.terminal_value = terminal_value
        self.suffix_linker = SuffixLinker()
        self.root = self.node_factory.create_root()

    def process_all_values(self):
        """Create suffix tree from values in the data source."""
        location = Location(self.root, self.data_store)
        try:
            while True:
                value, offset = self.get_next_value_and_offset()
                self.process_value(location, value, offset)
                #self.process_value(location, *self.get_next_value_and_offset())
        except StopIteration:
            self.finish(location)

    def final_id(self):
        return next(self.id_count)

    def get_next_value_and_offset(self):
        value,offset = next(self.data_generator)
        self.data_store.add(value)
        self.last_offset = offset
        return value,offset

    def finish(self, location):
        self.process_value(location, self.terminal_value, self.last_offset + 1)

    def process_value(self, location, value, offset):
        continue_processing_value = True
        while continue_processing_value and not location.follow_value(value):
            self.suffix_linker.needs_suffix_link(self.node_factory.create_leaf(location, value, offset))
            continue_processing_value = location.go_to_suffix()
            if location.next_edge_offset == 0:
                self.suffix_linker.link_to(location.node)


