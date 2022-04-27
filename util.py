class MemoryHandler:

    def __init__(self):
        self.reference_values = {}
        self.address = 1

    def get_value(self, address):
        if isinstance(self.reference_values[address], list):
            return self.reference_values[address][-1]
        else:
            return self.reference_values[address]

    def put_value(self, value, mutable):
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
