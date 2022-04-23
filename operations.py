from binop_state import StartBinOpState
from call_state import StartCallState

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

    def is_forward_completed(self, forward):
        return True


class ReturnOperation(Operation):

    def __init__(self, value):
        self.eval = None
        self.value = value
        Operation.__init__(self)

    def evaluate(self, evaluator):
        evaluator.evaluate_return(self)


class SliceOperation(Operation):

    def __init__(self, lower, higher, step):
        self.eval = None
        self.lower = lower
        self.higher = higher
        self.step = step
        Operation.__init__(self)

    def evaluate(self, evaluator):
        evaluator.evaluate_slice(self)

    def set_elements(self):
        self.eval = []
        while self.lower.eval < self.higher.eval:
            self.eval.append(self.lower.eval)
            self.lower.eval += self.step.eval


class SubscriptOperation(Operation):

    def __init__(self, slice, value):
        self.eval = None
        self.slice = slice
        self.value = value
        Operation.__init__(self)

    def evaluate(self, evaluator):
        evaluator.evaluate_subscript(self)

    def set_elements(self):
        self.eval = []
        for v in self.slice.eval:
            self.eval.append(self.value.eval[v])


class CompareOperation(Operation):

    def __init__(self, left, comparators, comparisons):
        self.eval = None
        self.left = left
        self.comparators = comparators
        self.comparisons = comparisons
        Operation.__init__(self)

    def evaluate(self, evaluator):
        evaluator.evaluate_compare(self)


class ListOperation(Operation):

    def __init__(self, elts):
        self.eval = None
        self.elts = elts
        Operation.__init__(self)

    def evaluate(self, evaluator):
        evaluator.evaluate_list(self)


class GlobalOperation(Operation):

    def __init__(self):
        Operation.__init__(self)

    def evaluate(self, evaluator):
        return


class BreakOperation(Operation):

    def __init__(self):
        Operation.__init__(self)

    def evaluate(self, evaluator):
        evaluator.evaluate_break(self)


class CallOperation(Operation):

    def __init__(self, function, args):
        self.function = function
        self.args = args
        self.state = StartCallState(self)
        Operation.__init__(self)

    def evaluate(self, evaluator):
        self.state.evaluate()


class BinaryOperation(Operation):

    def __init__(self, left, right, operation):
        self.left = left
        self.right = right
        self.operation = operation
        self.state = StartBinOpState(self)
        Operation.__init__(self)

    def evaluate(self, evaluator):
        self.state.evaluate()

class AssignOperation(Operation):

    def __init__(self, value, targets):
        self.eval = None
        self.value = value
        self.targets = targets
        Operation.__init__(self)

    def evaluate(self, evaluator):
        self.value.evaluate(evaluator)
        self.eval = self.value.eval
        evaluator.evaluate_assign(self)


class AugAssignOperation(Operation):

    def __init__(self, value):
        self.value = value
        self.target = None
        Operation.__init__(self)


class ReferenceOperation(Operation):

    def __init__(self, ref):
        self.eval = None
        self.ref = ref
        Operation.__init__(self)

    def evaluate(self, evaluator):
        evaluator.evaluate_name(self)


class ConstantOperation(Operation):

    def __init__(self, value):
        self.value = value
        Operation.__init__(self)

    def evaluate(self, evaluator):
        evaluator.evaluate_constant(self)


class CompositeOperation(Operation):

    def __init__(self):
        Operation.__init__(self)
        self.operations = []
        self.current = []

    def get_operation(self):
        return self.operations[self.current[-1]]

    def increment_current(self):
        if self.current[-1] < len(self.operations) - 1:
            self.current[-1] += 1

    def decrement_current(self):
        if self.current[-1] > 0:
            self.current[-1] -= 1

    def is_last(self):
        return self.current[-1] == len(self.operations) - 1

    def is_first(self):
        return self.current[-1] == 0

    def is_backward_completed(self):
        return True

    def initialize(self, forward):
        self.current.append(0)
        return True

    def finalize(self):
        self.current.pop()
        return

    def update_next(self):
        return

    def update_back(self):
        return

    def get_source(self):
        return self.parent_operation.get_source()


class IfThenElseOperation(CompositeOperation):

    def __init__(self, test):
        self.test = test
        self.choices_stack = []
        CompositeOperation.__init__(self)

    def get_operation(self):
        if self.choices_stack[-1] == 1:
            return self.operations[0][self.current[-1]]
        else:
            return self.operations[1][self.current[-1]]

    def initialize(self, forward):
        super(IfThenElseOperation, self).initialize(forward)
        if forward.visit(self.test):
            self.choices_stack.append(1)
        else:
            self.choices_stack.append(0)
        return True

    def finalize(self):
        super(IfThenElseOperation, self).finalize()
        self.choices_stack.pop()


class WhileOperation(CompositeOperation):

    def __init__(self, test):
        self.test = test
        self.number = []
        CompositeOperation.__init__(self)

    def is_forward_completed(self, forward):
        return not forward.visit(self.test)

    def is_backward_completed(self):
        return self.number[-1] == 0

    def initialize(self, forward):
        super(WhileOperation, self).initialize(forward)
        self.number.append(0)
        return forward.visit(self.test)

    def finalize(self):
        super(WhileOperation, self).finalize()
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
            self.get_source()[self.target].append(self.iter[-1][self.index[-1]])
        else:
            self.get_source()[self.target] = [self.iter[-1][self.index[-1]]]
        return True

    def finalize(self):
        super(ForOperation, self).finalize()
        self.index.pop()
        self.iter.pop()

    def update_next(self):
        self.current[-1] = 0
        self.index[-1] += 1
        self.get_source()[self.target].append(self.iter[-1][self.index[-1]])

    def update_back(self):
        self.current[-1] = len(self.operations) - 1
        self.index[-1] -= 1
        self.get_source()[self.target].pop()


class FunctionOperation(CompositeOperation):

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
        self.source = []
        self.index = -1
        self.operation = None
        CompositeOperation.__init__(self)

    def add(self, target, key):
        self.get_source()[target] = [key]

    def is_forward_completed(self, forward):
        if len(self.source) == 0:
            return False
        return 'return' in self.get_source()

    def initialize(self, forward):
        super(FunctionOperation, self).initialize(forward)
        self.index += 1
        self.update_operation(self)
        return True

    def finalize(self):
        super(FunctionOperation, self).finalize()
        self.source.pop(self.index)
        self.index -= 1

    def get_source(self):
        return self.source[self.index]

    def get_result(self):
        return self.get_source()['return']

    def remove_result(self):
        self.get_source().pop('return')

    def is_last(self):
        if self.operation.parent_operation == self:
            return super(FunctionOperation, self).is_last()
        return self.operation.parent_operation.is_last()

    def update_operation(self, parent):
        self.operation = parent.get_operation()

    def update_forward(self, forward):
        parent = self.update_forward_parent(forward)
        if parent:
            parent.increment_current()
            self.update_operation(parent)

    def update_forward_parent(self, forward):
        if self.operation.parent_operation.is_last():
            if isinstance(self.operation.parent_operation, FunctionOperation):
                return self.operation.parent_operation
            elif self.operation.parent_operation.is_forward_completed(forward):
                self.operation = self.operation.parent_operation
                return self.update_forward_parent(forward)
            else:
                self.operation.parent_operation.update_next()
                self.update_operation(self.operation.parent_operation)
                return None
        else:
            return self.operation.parent_operation

    def update_backward(self):
        parent = self.update_backward_parent()
        if parent:
            parent.decrement_current()
            self.update_operation(parent)

    def update_backward_parent(self):
        if not self.operation.parent_operation:
            return None
        if self.operation.parent_operation.is_first():
            if self.operation.parent_operation.is_backward_completed():
                self.operation.parent_operation.finalize()
                self.operation = self.operation.parent_operation
                return self.update_backward_parent()
            else:
                self.operation.parent_operation.update_back()
                self.update_operation(self.operation.parent_operation)
                return None
        else:
            return self.operation.parent_operation
