from suffix_tree.data_store import DataStore
from suffix_tree.location import Location
from itertools import count

from suffix_tree.visitor.visitor import OffsetAdjustingVisitor, NodeDFS, SuffixCollector


class SuffixTree:
    def __init__(self, root, data_store, final_suffix):
        self.root = root
        self.data_store = data_store
        self.final_suffix = final_suffix
        self.final_string = self.data_store.value_str(final_suffix, data_store.data_len())

    def uDO_set_start_offset(self, start_offset):
        dfs = NodeDFS()
        dfs(OffsetAdjustingVisitor(start_offset), self.root)

    def find_in_str(self, target_str, remaining_str):
        result = []
        start_offset = self.final_suffix
        while len(remaining_str) >= len(target_str):
            if target_str in remaining_str:
                found_index = remaining_str.index(target_str)
                result.append(found_index + start_offset)
                start_offset += found_index + 1
                remaining_str = remaining_str[found_index + 1:]
            else:
                break
        return result

    def find(self, target_str):
        result = self.find_in_str(target_str, self.final_string)
        location = Location(self.root, self.data_store)
        suffix_collector = SuffixCollector(result)
        for x in target_str:
            found_value = location.follow_value(x)
            if not found_value:
                return result
        nodeDFS = NodeDFS()
        nodeDFS(suffix_collector, location.node)
        return suffix_collector.suffixes

class TreeBuilder:
    def __init__(self, datasource, node_factory, terminal_value=-1):
        self.id_count = count()
        self.data_generator = ((val,offset) for (val,offset) in zip(datasource,self.id_count))
        self.node_factory = node_factory
        self.terminal_value = terminal_value
        self.data_store = DataStore()
        self.root = node_factory.create_root()

    def get_tree(self):
        return SuffixTree(self.root, self.data_store, self.final_suffix_offset)

    def process_all_values(self):
        """Create suffix tree from values in the data source."""
        location = Location(self.root, self.data_store)
        try:
            while True:
                self.process_value(location, *self.get_next_value_and_offset())
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
        self.final_location = location
        self.final_suffix_offset = self.node_factory.final_suffix()

    def process_value(self, location, value, offset):
        continue_processing_value = True
        while continue_processing_value:
            continue_processing_value = self.process_value_at_location(location, value, offset)

    def process_value_at_location(self, location, value, offset):
        """Process the value at the given location.

        Return:
            True if there is more processing to be done
            False otherwise
        """
        if location.follow_value(value):
            return False
        elif location.on_node:
            self.node_factory.create_leaf(location.node, value, offset)
            found_value = location.go_to_suffix()
            if location.on_node:
                self.node_factory.suffix_linker.link_to(location.node)
            return found_value
        else:
            new_node = self.node_factory.create_internal(
                    self.data_store.value_at(location.node.incoming_edge_start_offset),
                    location.node,
                    self.data_store.value_at(location.data_offset + 1),
                    location.data_offset)
            location.locate_on_node(new_node)
            return True
