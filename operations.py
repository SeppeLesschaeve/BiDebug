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

    def update_backward(self, call_stack):
        if self.current[-1] == 0 and self.is_backward_completed():
            self.finalize()
            call_stack.pop()
        else:
            if self.current[-1] == 0:
                self.update_back()
            else:
                self.current[-1] -= 1

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
        return self.parent_operation.get_source()

    def get_function(self):
        return self.parent_operation.get_function()


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
        self.index = []
        self.iter = []
        self.target = None
        self.iterName = None
        CompositeOperation.__init__(self)

    def is_forward_completed(self, forward):
        return self.index[-1] == len(self.iter[-1]) - 1

    def is_backward_completed(self):
        return self.index[-1] == 0

    def initialize(self, forward):
        super(ForOperation, self).initialize(forward)
        self.index.append(0)
        self.iter.append(forward.evaluate(self.iterName))
        if self.target in self.get_source():
            self.get_source()[self.target][-1] = self.iter[-1][self.index[-1]]
        else:
            self.get_source()[self.target] = [self.iter[-1][self.index[-1]]]

    def finalize(self):
        self.index.pop()
        self.iter.pop()

    def update_next(self):
        self.current[-1] = 0
        self.index[-1] += 1
        self.get_source()[self.target][-1] = self.iter[-1][self.index[-1]]

    def update_back(self):
        self.current[-1] = len(self.operations) - 1
        self.index[-1] -= 1
        self.get_source()[self.target][-1] = self.iter[-1][self.index[-1]]


class FunctionOperation(CompositeOperation):

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
        self.source = []
        self.result = None
        self.index = -1
        CompositeOperation.__init__(self)

    def initialize(self, forward):
        self.index += 1

    def finalize(self):
        self.arguments.pop(self.index)
        self.index -= 1

    def get_source(self):
        return self.source[self.index]

    def get_function(self):
        return self
