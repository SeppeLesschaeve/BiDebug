def is_composite(operation):
    return isinstance(operation, Operation) and operation.is_composite()


class Operation:

    def __init__(self):
        self.parent_operation = None

    def is_composite(self):
        return False


class CompositeOperation(Operation):

    def __init__(self):
        Operation.__init__(self)
        self.operations = []

    def current_operation(self, current):
        return self.operations[current]

    def update_forward(self, call_stack, forward):
        current = call_stack[-1]
        if current[1] == len(self.operations) - 1:
            if self.is_forward_completed(forward):
                if len(call_stack) > 1:
                    call_stack.append(call_stack[-2])
            else:
                current[0].update_next(call_stack, forward)
        else:
            current[1] += 1
            if is_composite(self.operations[current[1]]):
                if current[1] < len(self.operations) - 1:
                    current[1] += 1
                call_stack.append([self.operations[current[1]-1], 0])
                call_stack[-1].initialize(call_stack, forward)

    def update_backward(self, call_stack, reverse):
        current = call_stack[-1]
        if current[1] == 0:
            if self.is_backward_completed():
                current[0].finalize()
                call_stack.pop()
            else:
                current[0].update_back(call_stack, reverse)
        else:
            current[1] -= 1
            if is_composite(self.operations[current]):
                if current[1] > 0:
                    current[1] -= 1
                call_stack.pop()

    def is_composite(self):
        return True

    def is_forward_completed(self, forward):
        return True

    def is_backward_completed(self):
        return True

    def initialize(self, call_stack, forward):
        return

    def finalize(self):
        return

    def update_next(self, call_stack, forward):
        return

    def update_back(self, call_stack, reverse):
        return


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

    def initialize(self, call_stack, forward):
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

    def initialize(self, call_stack, forward):
        self.number.append(0)
        if not forward.visit(self.test):
            call_stack[-1][1] = len(self.operations) - 1

    def finalize(self):
        self.number.pop()

    def update_next(self, call_stack, forward):
        call_stack[-1][1] = 0
        self.number[-1] += 1

    def update_back(self, call_stack, reverse):
        self.number[-1] -= 1
        call_stack[-1][1] = len(self.operations) - 1


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

    def update_next(self, call_stack, forward):
        call_stack[-1][1] = 0
        self.index += 1
        forward.source[self.target] = self.iter[self.index]

    def update_back(self, call_stack, reverse):
        call_stack[-1][1] = len(self.operations) - 1
        self.index -= 1
        reverse.source[self.target] = self.iter[self.index]


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

