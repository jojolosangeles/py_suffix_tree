from suffix_tree.location import Location
from itertools import count
import re
from suffix_tree.visitor.visitor import NodeDFS, SuffixCollector
import time

class SuffixTree:
    def __init__(self, root, node_store, data_store, final_suffix):
        self.root = root
        self.node_store = node_store
        self.data_store = data_store
        self.final_suffix = final_suffix
        self.final_string = self.data_store.value_str(0, data_store.data_len() -1)

    def find_in_str(self, target_str, remaining_str):
        return [m.start() for m in re.finditer(target_str, remaining_str)]

    def find(self, target_str):
        location = Location(self.root, self.data_store)
        suffix_collector = SuffixCollector()
        for x in target_str:
            found_value = self.node_store.followValue(location, x)
            if not found_value:
                return []
        nodeDFS = NodeDFS()
        nodeDFS(suffix_collector, self.node_store, location.node)
        return suffix_collector.suffixes

class NodeStore:
    def __init__(self):
        self.PK_partition = {}  # key is PK, value is dictionary of SK to node

    def createPartition(self, key, node):
        self.PK_partition[key] = { node.SK: node }

    def addToPartition(self, key, SK, node):
        self.PK_partition[key][SK] = node

    def followValue(self, location, value):
        if location.on_node:
            partitionKey = location.node.PK
            if value in self.PK_partition[partitionKey]:
                location.node = self.PK_partition[partitionKey][value]
                location.on_node = location.node.incomingEdgeLength() == 1
                location.data_offset = 1
                return True
            else:
                return False
        elif location.node.is_leaf():
            # does the value match the value at the data_offset?
            result = location.data_store.value_at(location.data_offset + location.node.iESO) == value
            if result:
                location.data_offset += 1
            return result
        else:
            # internal value sequence
            testValue = location.node.incomingEdgeValueSequence[location.data_offset]
            if testValue == value:
                location.data_offset += 1
                if location.data_offset == len(location.node.incomingEdgeValueSequence):
                    location.on_node = True
                return True
        return False

    def children(self, partitionKey):
        partition = self.PK_partition[partitionKey]
        return [partition[child] for child in partition if child != "self"]

    def __repr__(self):
        result = ""
        for key in self.PK_partition:
            result += f"  {key}\n"
            partition = self.PK_partition[key]
            for k2 in partition:
                kpart = ""
                if k2 != "self":
                    kpart = f"{k2} -> "
                result += f"    {kpart}{partition[k2]}\n"
        return result

class TreeBuilder:
    """This class builds a suffix tree using the Ukkonen algorithm."""
    def __init__(self, data_generator, data_store, node_factory, node_store, terminal_value=-1):
        self.id_count = count()
        self.data_generator = data_generator
        self.node_factory = node_factory
        self.node_store = node_store
        self.terminal_value = terminal_value
        self.data_store = data_store
        self.root = node_factory.create_root()
        self.node_store.createPartition(self.root.PK, self.root)
        self.print_each_time_value_processed = True
        self.print_after_value_processing_complete = True

    def get_tree(self):
        return SuffixTree(self.root, self.node_store, self.data_store, self.final_suffix_offset)

    def process_all_values(self):
        """Create suffix tree from values in the data source."""
        location = Location(self.root, self.data_store)
        counter = 0
        mcounter = 0
        start_time = time.time()
        try:
            while True:
                self.process_value(location, *self.get_next_value_and_offset())
                counter += 1
                if (counter == 100000):
                    mcounter += 1
                    print("{} {}".format(mcounter,time.time()-start_time))
                    start_time = time.time()
                    counter = 0
        except StopIteration:
            self.last_offset += 1
            self.process_value(location, self.terminal_value, self.last_offset)
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

    def dbg_print(self, prefix, value, location):
        #if value == -1:
        print(prefix)
        print(self.node_store)
        print(f"  {self.node_factory.suffix_linker}")
        print(f"  {value}  Location {location}\n")

    def process_value(self, location, value, offset):
        print(f"Process {value}, offset {offset}")
        print(f"  Location {location}")
        continue_processing_value = True
        count = 0
        while continue_processing_value:
            continue_processing_value = self.process_value_at_location(location, value, offset)
            if self.print_each_time_value_processed:
                count += 1
                self.dbg_print(f"Step {count}: ", value, location)
        if self.print_after_value_processing_complete:
            self.dbg_print("Final", value, location)

    def process_value_at_location(self, location, value, offset):
        """Process the value at the given location.

        Return:
            True if there is more processing to be done
            False otherwise
        """
        # If the value can be found at the current location, no more processing is necessary
        if location.on_node:
            if self.node_store.followValue(location, value):
                return False
        else:
            # If the value matches, just change the location, and return False because no further value processing is needed.
            #
            # Otherwise, create an INTERNAL GraphNode, set the Location to that GraphNode, and return True
            # to indicate the value needs to be processed at the current Location.
            #
            # The Location is on an oncoming edge of either an INTERNAL or LEAF GraphNode.
            #
            # If the Location is on the oncoming edge of a Leaf, check the value based on iESO and location data_offset
            if location.node.is_leaf():
                if value == self.data_store.value_at(location.node.iESO + location.data_offset):
                    location.data_offset += 1
                    return False
            elif location.data_offset >= len(location.node.incomingEdgeValueSequence):
                print(f"ERROR, {location}, {location.node}, bad data_offset")
            elif value == location.node.incomingEdgeValueSequence[location.data_offset]:
                location.data_offset += 1
                if location.data_offset == len(location.node.incomingEdgeValueSequence):
                    location.on_node = True
                return False

        # if the value doesn't match, we have to inject it at the current location
        if location.on_node:
            leaf = self.node_factory.create_leaf(location.node, value, offset)
            self.node_store.addToPartition(location.node.PK, value, leaf)
            found_value = location.go_to_suffix(self.node_store)
            if found_value and location.on_node:
                self.node_factory.suffix_linker.link_to(location.node)
            return found_value
        else:
            # If the value matches, just change the location, and return False because no further value processing is needed.
            #
            # Otherwise, create an INTERNAL GraphNode, set the Location to that GraphNode, and return True
            # to indicate the value needs to be processed at the current Location.
            #
            # The Location is on an oncoming edge of either an INTERNAL or LEAF GraphNode.
            #
            # If the Location is on the oncoming edge of a Leaf, check the value based on iESO and location data_offset
            if location.node.is_leaf():
                self.create_internal_to_leaf(location)
                return True
            else:
                self.create_internal_node(location, location.node.incomingEdgeValueSequence[:location.data_offset],
                                              location.node.incomingEdgeValueSequence[location.data_offset])
                return True


    def create_internal_to_leaf(self, location):
        # just create an internal node, set location on that node, and keep processing
        incomingEdgeValueSequence = self.data_store.value_str(location.node.iESO, location.node.iESO + location.data_offset - 1)
        link_value = self.data_store.value_at(location.node.iESO + location.data_offset)
        self.create_internal_node(location, incomingEdgeValueSequence, link_value)

    def create_internal_node(self, location, incomingEdgeValueSequence, link_value):
        print(f"create_internal_node {location} \"{incomingEdgeValueSequence}\", link_value={link_value}")
        print(f"before: {id(location.node)} {location.node}")
        if incomingEdgeValueSequence == "ee":
            print("wait")
        # create node between 'location.node' and 'location.node.parent',
        # then set up parent links
        parent_node = location.node.parent
        child_node = location.node
        internal_node_to_insert_on_edge = self.node_factory.create_internal(incomingEdgeValueSequence)
        internal_node_to_insert_on_edge.parent = parent_node
        child_node.parent = internal_node_to_insert_on_edge
        child_node.PK = internal_node_to_insert_on_edge.PK

        # set up node_store partitions, a new Internal Node is a new partition
        self.node_store.createPartition(internal_node_to_insert_on_edge.PK, internal_node_to_insert_on_edge)
        self.node_store.addToPartition(parent_node.PK, incomingEdgeValueSequence[0], internal_node_to_insert_on_edge)
        self.node_store.addToPartition(internal_node_to_insert_on_edge.PK, link_value, child_node)

        if child_node.is_leaf():
            child_node.iESO += location.data_offset
        else:
            child_node.incomingEdgeValueSequence = child_node.incomingEdgeValueSequence[location.data_offset:]
        location.locate_on_node(internal_node_to_insert_on_edge)
        self.node_factory.suffix_linker.needs_suffix_link(internal_node_to_insert_on_edge)
        print(f"After Location {location}")
        print(f"After creating Internal Node: {location.node}")

