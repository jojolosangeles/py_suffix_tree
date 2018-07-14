
class DataStore:
    """Stores values as they are encountered, provides access to previous values"""
    def __init__(self):
        self.values = []

    def add(self, value):
        self.values.append(value)

    def value_str(self, start_offset, end_offset):
        if end_offset == -1:
            return ''.join(self.values[start_offset:])
        else:
            return ''.join(self.values[start_offset:end_offset + 1])

    def value_at(self, offset):
        try:
            return self.values[offset]
        except IndexError:
            print("Offset={}, number values={}".format(offset, len(self.values)))
            return 0





