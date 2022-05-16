class MemoryHandler:

    def __init__(self):
        self.reference_values = {}
        self.address = 1

    def is_immutable(self, value):
        return isinstance(value, tuple) or isinstance(value, int) or isinstance(value, float) or \
               isinstance(value, complex) or isinstance(value, str) or isinstance(value, bytes)

    def is_mutable(self, address):
        if isinstance(self.reference_values[address], list):
            return True
        else:
            return False

    def get_value(self, address):
        if isinstance(self.reference_values[address], list):
            return self.reference_values[address][-1]
        else:
            return self.reference_values[address]

    def put_value(self, value):
        if not self.is_immutable(value):
            self.put_value_typed(value, True)
        else:
            self.put_value_typed(value, False)

    def put_value_typed(self, value, mutable):
        if mutable:
            self.reference_values[self.address] = [value]
        else:
            self.reference_values[self.address] = value
        self.address += 1

    def inv_value(self, address):
        if isinstance(self.reference_values[address], list):
            if len(self.reference_values[address]) == 1:
                self.reference_values.pop(address)
                return True
            else:
                self.reference_values[address].pop()
                return False
        else:
            self.reference_values.pop(address)
            return True
