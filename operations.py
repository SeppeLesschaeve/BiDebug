def is_composite(operation):
    return isinstance(operation, Operation) and operation.is_composite()


class Operation:

    def __init__(self):
        self.parent_operation = None

    def update_next(self, call_stack, forward):
        if self.parent_operation is not None:
            self.parent_operation.update_next(call_stack, forward)

    def update_previous(self, call_stack, reverse):
        if self.parent_operation is not None:
            self.parent_operation.update_previous(call_stack, reverse)

    def is_composite(self):
        return False


class CompositeOperation(Operation):

    def __init__(self):
        Operation.__init__(self)
        self.operations = []
        self.current = []

    def current_operation(self):
        return self.operations[self.current[-1]]

    def update_next(self, call_stack, forward):
        if self.current[-1] == len(self.operations) - 1:
            call_stack.pop()
        else:
            self.current[-1] += 1
            if is_composite(self.operations[self.current[-1]]):
                call_stack.append(self.operations[self.current[-1]])

    def update_previous(self, call_stack, reverse):
        if self.current[-1] == 0:
            call_stack.pop()
        else:
            self.current[-1] -= 1
            if is_composite(self.operations[self.current[-1]]):
                call_stack.pop()

    def is_composite(self):
        return True


class IfThenElseOperation(CompositeOperation):

    def __init__(self):
        self.test = None
        self.choices_stack = []
        CompositeOperation.__init__(self)

    def initialize(self, forward):
        if forward.visit(self.test):
            self.choices_stack.append(1)
        else:
            self.choices_stack.append(0)

    def update_previous(self, call_stack, reverse):
        if self.current[-1] == 0:
            self.choices_stack.pop()
        super(IfThenElseOperation, self).update_previous(call_stack, reverse)

    def current_operation(self):
        if self.choices_stack[-1] == 1:
            return self.operations[0][self.current[-1]]
        else:
            return self.operations[1][self.current[-1]]


class WhileOperation(CompositeOperation):

    def __init__(self):
        self.test = None
        self.number = []
        CompositeOperation.__init__(self)

    def initialize(self, forward):
        self.number.append(0)
        if not forward.visit(self.test):
            self.current[-1] = len(self.operations) - 1

    def update_next(self, call_stack, forward):
        if self.current[-1] == len(self.operations) - 1 and forward.visit(self.test):
            self.current[-1] = 0
            self.number[-1] += 1
        else:
            super(WhileOperation, self).update_next(call_stack, forward)

    def update_previous(self, call_stack, reverse):
        if self.current[-1] == 0:
            if self.number[-1] > 0:
                self.current[-1] = len(self.operations) - 1
                self.number[-1] -= 1
            else:
                call_stack.pop()
        else:
            super(WhileOperation, self).update_previous(call_stack, reverse)


class ForOperation(CompositeOperation):

    def __init__(self):
        self.index = 0
        self.iter = None
        self.target = None
        CompositeOperation.__init__(self)

    def update_next(self, call_stack, forward):
        if self.current[-1] == len(self.operations) - 1 and self.index < len(self.iter) - 1:
            self.current[-1] = 0
            self.index += 1
            forward.source[self.target] = self.iter[self.index]
        else:
            super(ForOperation, self).update_next(call_stack, forward)

    def update_previous(self, call_stack, reverse):
        if self.current[-1] == 0:
            if self.index > 0:
                self.current[-1] = len(self.operations) - 1
                self.index -= 1
                reverse.source[self.target] = self.iter[self.index]
            else:
                call_stack.pop()
        else:
            super(ForOperation, self).update_previous(call_stack, reverse)


class FunctionOperation(CompositeOperation):

    def __init__(self):
        self.arguments = None
        CompositeOperation.__init__(self)

    def initialize(self):
        self.current.append(0)

    def set_arguments(self, args):
        self.arguments = args

