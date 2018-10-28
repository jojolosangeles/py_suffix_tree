import mmap
import os

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


class MmapDataStore:
    MAX_READ_SIZE=20

    """Stores values processed, provides access to previously processed values"""
    def __init__(self, filePath):
        self.filePath = filePath
        f = open(filePath, "r+b")
        self.mmfile = mmap.mmap(f.fileno(), 0)
        statinfo = os.stat(self.filePath)
        self.fileSize = statinfo.st_size

    def data_len(self):
        return self.fileSize

    def add(self, value):
        pass

    def get_values(self, start_offset, end_offset):
        return [value for value in self.mmfile[start_offset:(end_offset+1)]]

    def get_read_size(self, amount):
        if amount > self.MAX_READ_SIZE:
            return self.MAX_READ_SIZE
        else:
            return amount

    def value_str(self, start_offset, end_offset):
        if start_offset < 0 or start_offset >= self.fileSize:
            print("UNEXPECTED seek to invalid file location, start_offset={start_offset}, end_offset={end_offset}"
                  .format(start_offset=start_offset, end_offset=end_offset))
            return ""
        self.mmfile.seek(start_offset)
        if end_offset == -1:
            return self.mmfile.read(self.get_read_size(self.fileSize - start_offset))
        else:
            return self.mmfile.read(self.get_read_size(end_offset - start_offset + 1))

    def value_at(self, offset):
        try:
            return self.mmfile[offset]
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

# from https://stackoverflow.com/questions/2988211/how-to-read-a-single-character-at-a-time-from-a-file-in-python
def chunks(filename, buffer_size=4096):
    """Reads `filename` in chunks of `buffer_size` bytes and yields each chunk
    until no more characters can be read; the last chunk will most likely have
    less than `buffer_size` bytes.

    :param str filename: Path to the file
    :param int buffer_size: Buffer size, in bytes (default is 4096)
    :return: Yields chunks of `buffer_size` size until exhausting the file
    :rtype: str

    """
    with open(filename, "rb") as fp:
        chunk = fp.read(buffer_size)
        while chunk:
            yield chunk
            chunk = fp.read(buffer_size)

def file_chars_with_offset(filename, buffersize=4096):
    """Yields the contents of file `filename` character-by-character. Warning:
    will only work for encodings where one character is encoded as one byte.

    :param str filename: Path to the file
    :param int buffer_size: Buffer size for the underlying chunks,
    in bytes (default is 4096)
    :return: Yields the contents of `filename` character-by-character.
    :rtype: char

    """
    offset = 0
    for chunk in chunks(filename, buffersize):
        for char in chunk:
            yield char,offset
            offset += 1
