def is_composite(operation):
    return isinstance(operation, Operation) and operation.is_composite()

add = lambda a, b: a + b
sub = lambda a, b: a - b
mul = lambda a, b: a * b
div = lambda a, b: a / b
en = lambda a, b: a and b
of = lambda a, b: a or b
niet = lambda a: not a
eq = lambda a, b: a == b
neq = lambda a, b: a != b
lt = lambda a, b: a < b
lte = lambda a, b: a <= b
gt = lambda a, b: a > b
gte = lambda a, b: a >= b
inn = lambda a, b: a in b
nin = lambda a, b: a not in b
iss = lambda a, b: a is b
nis = lambda a, b: a is not b

class Operation:

    def __init__(self):
        self.parent_operation = None

    def is_composite(self):
        return False


class CompositeOperation(Operation):

    def __init__(self):
        Operation.__init__(self)
        self.operations = []
        self.current = []

    def current_operation(self, current):
        return self.operations[current]

    def update_forward(self, call_stack, forward):
        if self.current[-1] == len(self.operations) - 1:
            if self.is_forward_completed(forward):
                parent = self.parent_operation
                if parent:
                    call_stack.append(parent)
                    if parent.current[-1] < len(parent.operations) - 1:
                        parent.current[-1] += 1
            else:
                self.update_next()
        else:
            self.current[-1] += 1
            new_current = self.operations[self.current[-1]]
            if is_composite(new_current):
                call_stack.append(new_current)
                new_current.initialize(forward)
                while is_composite(new_current.operations[0]):
                    call_stack.append(new_current.operations[0])
                    new_current = new_current.operations[0]
                    new_current.initialize(forward)

    def update_backward(self, call_stack):
        parent = self
        while parent.current[-1] == 0 and parent.is_backward_completed():
            parent.finalize()
            call_stack.pop()
            parent = parent.parent_operation
        else:
            if parent.current[-1] == 0:
                parent.update_back()
            else:
                parent.current[-1] -= 1
                if is_composite(parent.operations[parent.current[-1]]):
                    call_stack.pop()

    def is_composite(self):
        return True

    def is_forward_completed(self, forward):
        return True

    def is_backward_completed(self):
        return True

    def initialize(self, forward):
        self.current.append(0)

    def finalize(self):
        return

    def update_next(self):
        return

    def update_back(self):
        return

    def get_source(self):
        return self.parent_operation.get_source()[-1]


class IfThenElseOperation(CompositeOperation):

    def __init__(self):
        self.test = None
        self.choices_stack = []
        CompositeOperation.__init__(self)

    def current_operation(self, current):
        if self.choices_stack[-1] == 1:
            return self.operations[0][current]
        else:
            return self.operations[1][current]

    def initialize(self, forward):
        super(IfThenElseOperation, self).initialize(forward)
        if forward.visit(self.test):
            self.choices_stack.append(1)
        else:
            self.choices_stack.append(0)

    def finalize(self):
        self.choices_stack.pop()


class WhileOperation(CompositeOperation):

    def __init__(self):
        self.test = None
        self.number = []
        CompositeOperation.__init__(self)

    def is_forward_completed(self, forward):
        return not forward.visit(self.test)

    def is_backward_completed(self):
        return self.number[-1] == 0

    def initialize(self, forward):
        super(WhileOperation, self).initialize(forward)
        self.number.append(0)
        if not forward.visit(self.test):
            self.current[-1] = len(self.operations) - 1

    def finalize(self):
        self.number.pop()

    def update_next(self):
        self.current[-1] = 0
        self.number[-1] += 1

    def update_back(self):
        self.number[-1] -= 1
        self.current[-1] = len(self.operations) - 1


class ForOperation(CompositeOperation):

    def __init__(self):
        self.index = 0
        self.iter = None
        self.target = None
        CompositeOperation.__init__(self)

    def is_forward_completed(self, forward):
        return self.index == len(self.iter) - 1

    def is_backward_completed(self):
        return self.index == 0

    def update_next(self):
        self.current[-1] = 0
        self.index += 1
        self.get_source()[self.target] = self.iter[self.index]

    def update_back(self):
        self.current[-1] = len(self.operations) - 1
        self.index -= 1
        self.get_source()[self.target] = self.iter[self.index]


class FunctionOperation(CompositeOperation):

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
        self.source = []
        CompositeOperation.__init__(self)

    def set_arguments(self, args):
        self.arguments = args

    def finalize(self):
        self.arguments.pop()

    def get_source(self):
        return self.source[-1]
