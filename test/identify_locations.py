import sys

class FNode:

    def __init__(self, parent_id=None, incoming_sequence_id=None, suffix_locations=None):
        self.parent_id = parent_id
        self.incoming_sequence_id = incoming_sequence_id
        self.suffix_locations = suffix_locations

    def include_suffix_offset(self, suffix_offset, nodes):
        if self.suffix_locations != None:
            self.suffix_locations.append(suffix_offset)
        if self.parent_id in nodes:
            nodes[self.parent_id].include_suffix_offset(suffix_offset, nodes)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python identify_locations.py <weighted_dictionary_file> <flat_tree_file>")
        exit()

    weighted_dictionary_file = sys.argv[1]
    flat_tree_file = sys.argv[2]
    id_to_sequence = {}
    id_to_weight = {}

    with open(weighted_dictionary_file, "r") as dict_fp:
        for line in dict_fp:
            data = line.strip().split(" ")
            if len(data) == 3:
                id = int(data[0])
                sequence = data[1]
                weight = int(data[2])
                id_to_sequence[id] = sequence
                id_to_weight[id] = weight

    sequence_id_scores = {}

    summary_file_name = "{}.summary".format(flat_tree_file)
    selected_sequence_ids = set()
    with open(summary_file_name, "w") as output:
        with open(flat_tree_file, "r") as tree_fp:
            for line in tree_fp:
                data = line.strip().split(" ")
                # I {id} {parent_id} {incoming_sequence_id} {leaf_count} {depth}
                if len(data) == 6 and data[0] == "I":
                    leaf_count = int(data[4])
                    depth = int(data[5])
                    sequence_id = int(data[3])
                    if sequence_id in id_to_weight:
                        selected_sequence_ids.add(sequence_id)
                        output.write("{id} {sequence} {depth} {leaf_count}\n".format(
                            id=sequence_id,
                            sequence=id_to_sequence[sequence_id],
                            depth=depth,
                            leaf_count=leaf_count
                        ))

    nodes = {}
    node_locations_in_sequence = {}  # key=node_id, value=set of locations
    sequence_locations = {}
    with open(flat_tree_file, "r") as tree_fp:
        for line in tree_fp:
            data = line.strip().split(" ")
            # R {id}
            # I {id} {parent_id} {incoming_sequence_id} {leaf_count} {depth}
            # L {id} {parent_id} {incoming_sequence_id} {suffix_offset}
            if len(data) == 6 and data[0] == "I":
                id = int(data[1])
                parent_id = int(data[2])
                incoming_sequence_id = int(data[3])
                leaf_count = int(data[4])
                depth = int(data[5])
                sequence_location_list = sequence_locations[incoming_sequence_id] \
                    if incoming_sequence_id in sequence_locations \
                    else [] if incoming_sequence_id in selected_sequence_ids \
                    else None
                if sequence_location_list is not None:
                    sequence_locations[incoming_sequence_id] = sequence_location_list
                nodes[id] = FNode(parent_id, incoming_sequence_id, sequence_location_list)
            elif len(data) == 5 and data[0] == "L":
                id = int(data[1])
                parent_id = int(data[2])
                incoming_sequence_id = int(data[3])
                suffix_offset = int(data[4])
                nodes[id] = FNode(parent_id, incoming_sequence_id)
                nodes[parent_id].include_suffix_offset(suffix_offset, nodes)
            elif len(data) == 2 and data[0] == "R":
                id = int(data[1])
                nodes[id] = FNode()

    sequence_location_file = "{}.locations".format(flat_tree_file)
    with open(sequence_location_file, "w") as seq_loc_output:
        for id,locations in sequence_locations.items():
            if len(locations) < 10:
                seq_loc_output.write("{sequence} {locations}\n".format(id=id,sequence=id_to_sequence[id],locations=locations))