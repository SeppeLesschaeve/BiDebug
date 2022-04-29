from binop_state import StartBinOpState
from call_state import StartCallState
from util import MemoryHandler

add = lambda a, b: a + b
sub = lambda a, b: a - b
mul = lambda a, b: a * b
div = lambda a, b: a / b
enn = lambda a, b: a and b
off = lambda a, b: a or b
nit = lambda a: not a
equ = lambda a, b: a == b
neq = lambda a, b: a != b
lth = lambda a, b: a < b
lte = lambda a, b: a <= b
gth = lambda a, b: a > b
gte = lambda a, b: a >= b
inn = lambda a, b: a in b
nin = lambda a, b: a not in b
iss = lambda a, b: a is b
isn = lambda a, b: a is not b


class BackwardException(Exception):

    def __init__(self):
        super(BackwardException, self).__init__('Chewbacka')


class BreakException(Exception):

    def __init__(self):
        super(BreakException, self).__init__('Obreaki-wan')


class CallException(Exception):

    def __init__(self, operation):
        self.operation = operation
        super(CallException, self).__init__('Callrisian')


class ReturnException(Exception):

    def __init__(self):
        super(ReturnException, self).__init__('Reyturn')


class Operation:

    memory_handler = MemoryHandler()

    def __init__(self):
        self.parent_operation = None

    def is_ready(self):
        return False

    def get_current_operation(self):
        return None

    def evaluate(self):
        return

    def finish_evaluation(self):
        return

    def revert_evaluation(self):
        return

    def get_function(self):
        return self.parent_operation.get_function()


class SingleOperation(Operation):

    def __init__(self):
        self.eval = []
        Operation.__init__(self)

    def is_ready(self):
        return self.eval

    def is_started(self):
        return not self.is_ready()

    def get_current_operation(self):
        return self

    def evaluate(self):
        return

    def finish_evaluation(self):
        return

    def revert_evaluation(self):
        self.eval.pop()

    def get_value(self):
        if self.eval:
            return self.eval[0]
        return None


class ComplexOperation(Operation):

    def __init__(self, operations):
        self.index = []
        self.operations = operations
        Operation.__init__(self)

    def get_index(self):
        return self.index[-1]

    def is_ready(self):
        return self.get_index() == len(self.operations) - 1 and self.get_current_operation().is_ready()

    def is_started(self):
        if not self.index:
            return True
        return self.get_index() == 0 and self.get_current_operation().is_started()

    def get_current_operation(self):
        return self.operations[self.get_index()].get_current_operation()

    def evaluate(self):
        if self.is_started():
            self.index.append(0)
        self.get_current_operation().evaluate()
        if self.get_current_operation().is_ready():
            self.get_current_operation().finish_evaluation()
            if not self.is_ready():
                self.index[-1] += 1

    def finish_evaluation(self):
        return

    def revert_evaluation(self):
        if not self.is_started():
            self.get_current_operation().revert_evaluation()
            if self.get_current_operation().is_started() and self.get_index() > 0:
                self.index[-1] -= 1

    def get_value(self):
        if self.is_ready():
            return self.get_current_operation().get_value()
        return None

    def handle_back(self):
        if not self.is_started():
            self.index[-1] -= 1
            self.revert_evaluation()

    def handle_break(self):
        if not self.is_ready():
            self.index[-1] += 1


class BreakOperation(SingleOperation):

    def __init__(self):
        SingleOperation.__init__(self)

    def evaluate(self):
        raise BreakException


class ConstantOperation(SingleOperation):

    def __init__(self, value):
        self.value = value
        SingleOperation.__init__(self)

    def evaluate(self):
        self.eval.append(self.value)


class NameOperation(SingleOperation):

    def __init__(self, name):
        self.name = name
        SingleOperation.__init__(self)

    def evaluate(self):
        self.eval.append(self.get_referenced_value())

    def get_referenced_value(self):
        return self.get_function().get_referenced_value(self.name)


class ReturnOperation(ComplexOperation):

    def __init__(self, operations):
        ComplexOperation.__init__(self, operations)

    def is_ready(self):
        if self.operations:
            super(ReturnOperation, self).is_ready()
        return True

    def is_started(self):
        if self.operations:
            return self.operations[0].is_started()
        return True

    def evaluate(self):
        if self.operations:
            super(ReturnOperation, self).evaluate()

    def finish_evaluation(self):
        if self.operations:
            self.get_function().add_result(self.get_current_operation().get_value())
        else:
            self.get_function().add_result(None)
        raise ReturnException

    def revert_evaluation(self):
        if self.operations:
            self.operations[0].eval.pop()

    def get_value(self):
        if self.operations:
            return super(ReturnOperation, self).get_value()
        else:
            return None


class BinaryOperation(ComplexOperation):

    def __init__(self, op, operations):
        self.op = op
        self.eval = []
        ComplexOperation.__init__(self, operations)

    def finish_evaluation(self):
        self.eval.append(self.op(self.operations[0].get_value(), self.operations[1].get_value()))

    def revert_evaluation(self):
        super(BinaryOperation, self).revert_evaluation()
        if self.is_started():
            self.eval.pop()

    def get_value(self):
        if self.is_ready():
            return self.eval[0]
        return None


class BooleanOperation(ComplexOperation):

    def __init__(self, op, operations):
        self.op = op
        self.eval = []
        ComplexOperation.__init__(self, operations)

    def finish_evaluation(self):
        self.eval.append(self.op(self.operations[0].get_value(), self.operations[1].get_value()))

    def revert_evaluation(self):
        super(BooleanOperation, self).revert_evaluation()
        if self.is_started():
            self.eval.pop()

    def get_value(self):
        if self.is_ready():
            return self.eval[0]
        return None


class CompareOperation(ComplexOperation):

    def __init__(self, comparisons, operations):
        self.comparisons = comparisons
        self.eval = []
        ComplexOperation.__init__(self, operations)

    def finish_evaluation(self):
        value = True
        for i in range(len(self.comparisons)):
            value = value and self.comparisons[i](self.operations[i].get_value(), self.operations[i + 1].get_value())
        self.eval.append(value)

    def revert_evaluation(self):
        super(CompareOperation, self).revert_evaluation()
        if self.is_started():
            self.eval.pop()

    def get_value(self):
        if self.is_ready():
            return self.eval[0]
        return False


class SubscriptOperation(ComplexOperation):

    def __init__(self, operations):
        self.eval = []
        ComplexOperation.__init__(self, operations)

    def finish_evaluation(self):
        self.eval.append(self.operations[0].get_value()[self.operations[1].get_value()])

    def revert_evaluation(self):
        super(SubscriptOperation, self).revert_evaluation()
        if self.is_started():
            self.eval.pop()

    def get_value(self):
        if self.is_ready():
            return self.eval[0]
        return False


class AugAssignOperation(ComplexOperation):

    def __init__(self, target, operations):
        self.target = target
        ComplexOperation.__init__(self, operations)

    def finish_evaluation(self):
        self.get_function().update_target(self.target, self.get_current_operation().get_value())

    def revert_evaluation(self):
        super(AugAssignOperation, self).revert_evaluation()
        if self.is_started():
            self.get_function().revert_target(self.target)


class AssignOperation(ComplexOperation):

    def __init__(self, targets, operations):
        self.targets = targets
        ComplexOperation.__init__(self, operations)

    def finish_evaluation(self):
        self.get_function().update_targets(self.targets, self.get_current_operation().get_value())

    def revert_evaluation(self):
        super(AssignOperation, self).revert_evaluation()
        if self.is_started():
            self.get_function().revert_targets(self.targets)


class ListOperation(ComplexOperation):

    def __init__(self, operations):
        self.eval = []
        ComplexOperation.__init__(self, operations)

    def is_ready(self):
        if self.operations:
            super(ListOperation, self).is_ready()
        return True

    def finish_evaluation(self):
        value = []
        for i in range(len(self.operations)):
            value.append(self.operations[i].get_value())
        self.eval.append(value)

    def evaluate(self):
        if self.operations:
            super(ListOperation, self).evaluate()

    def revert_evaluation(self):
        super(ListOperation, self).revert_evaluation()
        if self.is_started():
            self.eval.pop()

    def get_value(self):
        if self.is_ready():
            return self.eval[0]
        return False


class SetOperation(ComplexOperation):

    def __init__(self, operations):
        self.eval = []
        ComplexOperation.__init__(self, operations)

    def is_ready(self):
        if self.operations:
            super(SetOperation, self).is_ready()
        return True

    def finish_evaluation(self):
        value = set()
        for i in range(len(self.operations)):
            value.add(self.operations[i].get_value())
        self.eval.append(value)

    def evaluate(self):
        if self.operations:
            super(SetOperation, self).evaluate()

    def revert_evaluation(self):
        super(SetOperation, self).revert_evaluation()
        if self.is_started():
            self.eval.pop()

    def get_value(self):
        if self.is_ready():
            return self.eval[0]
        return False


class DictOperation(ComplexOperation):

    def __init__(self, keys, operations):
        self.keys = keys
        self.eval = []
        ComplexOperation.__init__(self, operations)

    def is_ready(self):
        if self.operations:
            super(DictOperation, self).is_ready()
        return True

    def finish_evaluation(self):
        value = {}
        for i in range(len(self.operations)):
            value[self.keys[i]] = self.operations[i].get_value()
        self.eval.append(value)

    def evaluate(self):
        if self.operations:
            super(DictOperation, self).evaluate()

    def revert_evaluation(self):
        super(DictOperation, self).revert_evaluation()
        if self.is_started():
            self.eval.pop()

    def get_value(self):
        if self.is_ready():
            return self.eval[0]
        return False


class WhileOperation(ComplexOperation):

    def __init__(self, operations):
        self.number = []
        ComplexOperation.__init__(self, operations)

    def is_ready(self):
        return self.get_index() == 0 and not self.operations[0].get_value()

    def is_started(self):
        return super(WhileOperation, self).is_started() and self.number[-1] == 0

    def evaluate(self):
        self.get_current_operation().evaluate()
        if self.is_ready():
            raise BreakException
        if self.get_index() == 0 and self.operations[0].get_value():
            self.index[-1] += 1
        elif self.get_current_operation().is_ready():
            self.get_current_operation().finish_evaluation()
            if self.get_index() < len(self.operations) - 1:
                self.index[-1] += 1
            else:
                self.finish_evaluation()

    def finish_evaluation(self):
        self.number[-1] += 1
        self.index[-1] = 0

    def revert_evaluation(self):
        if self.is_started():
            raise BackwardException
        if self.get_index() == 0 and self.number[-1] > 0:
            self.number[-1] -= 1
            self.index[-1] = len(self.operations) - 1
        else:
            self.get_current_operation().revert_evaluation()
            if self.get_current_operation().is_started() and self.get_index() > 0:
                self.index[-1] -= 1

    def get_value(self):
        return None


class ForOperation(ComplexOperation):

    def __init__(self, target, operations):
        self.get_function().update_target(target, None)
        self.target = target
        self.iterations = []
        ComplexOperation.__init__(self, operations)

    def is_ready(self):
        return super(ForOperation, self).is_ready() \
               and self.iterations[-1] == len(self.operations[0].get_value()) - 1

    def evaluate(self):
        if self.get_index() == 0:
            self.iterations.append(-1)
        self.get_current_operation().evaluate()
        if self.get_index() == 0:
            self.get_function().update_target(self.target, self.operations[0].get_value()[self.iterations[-1]])
        if super(ForOperation, self).is_ready():
            if not self.is_ready():
                self.iterations[-1] += 1
                self.get_function().update_target(self.target, self.operations[0].get_value()[self.iterations[-1]])
                self.index[-1] += 1

    def revert_evaluation(self):
        if self.is_started():
            raise BreakException
        self.get_current_operation().revert_evaluation()
        if self.get_index() == 1 and self.get_current_operation().is_started():
            if self.iterations[-1] > 0:
                self.iterations[-1] -= 1
                self.get_function().revert_target(self.target)
                self.index[-1] = len(self.operations) - 1
        elif self.get_current_operation().is_started():
            self.index[-1] -= 1

    def get_value(self):
        return None


class IfThenElseOperation(ComplexOperation):

    def __init__(self, operations):
        self.choices = []
        self.part_index = []
        self.then_part = operations[1]
        self.else_part = operations[2]
        ComplexOperation.__init__(self, operations)
        self.index.append(0)

    def get_index(self):
        if super(IfThenElseOperation, self).get_index() == 0:
            return 0
        else:
            return self.part_index[-1]

    def is_ready(self):
        if self.part_index:
            if self.choices[-1]:
                return self.get_index() == len(self.then_part) and self.get_current_operation().is_ready()
            else:
                return self.get_index() == len(self.else_part) and self.get_current_operation().is_ready()
        return False

    def is_started(self):
        if not self.part_index:
            return True
        return self.get_index() == 0 and self.get_current_operation().is_started()

    def get_current_operation(self):
        if self.get_index() == 0:
            return self.operations[0].get_current_operation()
        elif self.choices[-1]:
            return self.operations[1][self.get_index()].get_current_operation()
        else:
            return self.operations[2][self.get_index()].get_current_operation()

    def get_last_index(self):
        if self.choices[-1]:
            return len(self.operations[1])
        else:
            return len(self.operations[2])

    def evaluate(self):
        self.get_current_operation().evaluate()
        if self.is_ready():
            raise BreakException
        if self.get_index() == 0 and self.get_current_operation().is_ready():
            self.choices.append(self.get_current_operation().get_value())
            self.part_index.append(0)
            self.index[-1] = 1
        elif self.get_current_operation().is_ready():
            self.get_current_operation().finish_evaluation()
            if self.get_index() < self.get_last_index():
                self.part_index[-1] += 1

    def revert_evaluation(self):
        if self.is_started():
            raise BackwardException
        if self.get_index() == 0 and self.get_current_operation() != self.operations[0]:
            self.choices.pop()
            self.index[-1] = 0
        else:
            self.get_current_operation().revert_evaluation()
            if self.get_current_operation().is_started() and self.get_index() > 0:
                self.index[-1] -= 1

    def get_value(self):
        return None

    def handle_back(self):
        if not self.is_started():
            self.part_index[-1] -= 1
            self.revert_evaluation()









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
