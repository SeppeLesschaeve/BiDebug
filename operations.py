import copy

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
source_creator = None


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
    source_creator = None

    def __init__(self):
        self.parent_operation = None

    def is_mutable(self):
        return False

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

    def get_call(self):
        return self.parent_operation.get_call()


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
        return self.get_index() == 0 and self.get_current_operation().is_started()

    def get_current_operation(self):
        return self.operations[self.get_index()].get_current_operation()

    def evaluate(self):
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

    def is_mutable(self):
        if self.eval:
            address = Operation.get_call(self).mapping[self.name]
            return Operation.memory_handler.is_mutable(address)
        else:
            super(NameOperation, self).is_mutable()

    def evaluate(self):
        self.eval.append(self.get_referenced_value())

    def get_referenced_value(self):
        return self.get_call().get_referenced_value(self.name)


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
            self.get_call().add_result(self.get_current_operation().get_value())
        else:
            self.get_call().add_result(None)
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

    def evaluate(self):
        while not self.is_ready():
            super(BinaryOperation, self).evaluate()

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

    def evaluate(self):
        while not self.is_ready():
            super(BooleanOperation, self).evaluate()

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

    def evaluate(self):
        while not self.is_ready():
            super(CompareOperation, self).evaluate()

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

    def evaluate(self):
        while not self.is_ready():
            super(SubscriptOperation, self).evaluate()

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
        if self.get_current_operation().is_mutable():
            self.get_call().update_target(self.target, self.get_current_operation().get_value(), True)
        else:
            self.get_call().update_target(self.target, self.get_current_operation().get_value(), False)

    def revert_evaluation(self):
        super(AugAssignOperation, self).revert_evaluation()
        if self.is_started():
            self.get_call().revert_target(self.target)


class AssignOperation(ComplexOperation):

    def __init__(self, targets, operations):
        self.targets = targets
        ComplexOperation.__init__(self, operations)

    def finish_evaluation(self):
        if self.get_current_operation().is_mutable():
            self.get_call().update_targets(self.targets, self.get_current_operation().get_value(), True)
        else:
            self.get_call().update_targets(self.targets, self.get_current_operation().get_value(), False)

    def revert_evaluation(self):
        super(AssignOperation, self).revert_evaluation()
        if self.is_started():
            self.get_call().revert_targets(self.targets)


class ListOperation(ComplexOperation):

    def __init__(self, operations):
        self.eval = []
        ComplexOperation.__init__(self, operations)

    def is_mutable(self):
        return True

    def evaluate(self):
        if not self.operations:
            return
        while not self.is_ready():
            super(ListOperation, self).evaluate()

    def is_ready(self):
        if self.operations:
            super(ListOperation, self).is_ready()
        return True

    def finish_evaluation(self):
        value = []
        for i in range(len(self.operations)):
            value.append(self.operations[i].get_value())
        self.eval.append(value)

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

    def is_mutable(self):
        return True

    def is_ready(self):
        if self.operations:
            super(SetOperation, self).is_ready()
        return True

    def evaluate(self):
        if not self.operations:
            return
        while not self.is_ready():
            super(SetOperation, self).evaluate()

    def finish_evaluation(self):
        value = set()
        for i in range(len(self.operations)):
            value.add(self.operations[i].get_value())
        self.eval.append(value)

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

    def is_mutable(self):
        return True

    def is_ready(self):
        if self.operations:
            super(DictOperation, self).is_ready()
        return True

    def evaluate(self):
        if not self.operations:
            return
        while not self.is_ready():
            super(DictOperation, self).evaluate()

    def finish_evaluation(self):
        value = {}
        for i in range(len(self.operations)):
            value[self.keys[i]] = self.operations[i].get_value()
        self.eval.append(value)

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
            if self.get_current_operation().is_mutable():
                self.get_call().update_target(self.target, self.operations[0].get_value()[self.iterations[-1]], True)
            else:
                self.get_call().update_target(self.target, self.operations[0].get_value()[self.iterations[-1]], False)
        if super(ForOperation, self).is_ready():
            if not self.is_ready():
                self.iterations[-1] += 1
                if self.get_current_operation().is_mutable():
                    self.get_call().update_target(self.target, self.operations[0].get_value()[self.iterations[-1]], True)
                else:
                    self.get_call().update_target(self.target, self.operations[0].get_value()[self.iterations[-1]], False)
                self.index[-1] += 1

    def revert_evaluation(self):
        if self.is_started():
            raise BreakException
        self.get_current_operation().revert_evaluation()
        if self.get_index() == 1 and self.get_current_operation().is_started():
            if self.iterations[-1] > 0:
                self.iterations[-1] -= 1
                self.get_call().revert_target(self.target)
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


class AttributeOperation(ComplexOperation):

    def __init__(self, target, attr, operations):
        self.target = target
        self.attr = attr
        ComplexOperation.__init__(self, operations)

    def finish_evaluation(self):
        address = Operation.source_creator.get_prev_call().mapping[self.target][-1]
        value = Operation.memory_handler.reference_values[address][-1]
        copy_value = copy.deepcopy(value)
        Operation.memory_handler.reference_values[address].append(copy_value)
        arguments = []
        for i in range(len(self.operations)):
            arguments.append(self.operations[i].get_value())
        address = Operation.source_creator.get_prev_call().mapping[self.target][-1]
        value = Operation.memory_handler.reference_values[address][-1]
        getattr(value, self.attr)(*arguments)

    def revert_evaluation(self):
        if not self.is_started():
            super(AttributeOperation, self).revert_evaluation()
        else:
            Operation.source_creator.get_prev_call().revert_target(self.target)


class BuiltinOperation(ComplexOperation):

    def __init__(self, attr, operations):
        self.attr = attr
        self.eval = []
        ComplexOperation.__init__(self, operations)

    def finish_evaluation(self):
        arguments = []
        for i in range(len(self.operations)):
            arguments.append(self.operations[i].get_value())
        self.eval.append(getattr(__builtins__, self.attr)(*arguments))

    def revert_evaluation(self):
        self.eval.pop()

    def get_value(self):
        if not self.eval:
            return self.eval[-1]
        else:
            return None


class CallOperation(ComplexOperation):

    def __init__(self, name, args, operations):
        self.name = name
        self.args = args
        self.mapping = {}
        ComplexOperation.__init__(self, operations)

    def evaluate_mapping(self):
        self.args[len(self.mapping)].evaluate()
        if self.args[len(self.mapping)].is_ready():
            if isinstance(self.args[len(self.mapping)], NameOperation):
                address = Operation.source_creator.get_prev_call().mapping[self.args[len(self.mapping)].name][-1]
                if Operation.memory_handler.is_mutable(address):
                    value = copy.deepcopy(Operation.memory_handler.reference_values[address])
                else:
                    value = [Operation.memory_handler.reference_values[address][-1]]
            else:
                if isinstance(self.args[len(self.mapping)], ConstantOperation):
                    Operation.memory_handler.put_value(self.args[len(self.mapping)], False)
                else:
                    Operation.memory_handler.put_value(self.args[len(self.mapping)], True)
                value = [Operation.memory_handler.address]
            key = Operation.source_creator.functions[self.name].args[len(self.mapping)]
            self.mapping[key] = value

    def evaluate(self):
        while len(self.mapping) < len(self.args):
            self.evaluate_mapping()
        super(CallOperation, self).evaluate()

    def revert_evaluation(self):
        if self.is_started():
            self.mapping.clear()
        else:
            super(CallOperation, self).revert_evaluation()

    def get_referenced_value(self, name):
        return Operation.memory_handler.get_value(self.mapping[name][-1])

    def update_target(self, target, value, mutable):
        if target not in self.mapping:
            Operation.memory_handler.put_value(value, mutable)
            self.mapping[target] = [Operation.memory_handler.address]
            return
        address = self.mapping[target][-1]
        if Operation.memory_handler.is_mutable(address):
            Operation.memory_handler.reference_values[address].append(value)
        else:
            Operation.memory_handler.put_value(value, False)
            self.mapping[target].append(Operation.memory_handler.address)

    def update_targets(self, targets, value, mutable):
        if len(targets) == 1:
            self.update_target(targets[0], value, mutable)
        else:
            for i in range(len(targets)):
                self.update_target(targets[i], mutable)

    def revert_target(self, target):
        address = self.mapping[target][-1]
        if Operation.memory_handler.inv_value(address):
            self.mapping[target].pop()
            if not self.mapping:
                self.mapping.pop(target)

    def revert_targets(self, targets):
        for target in targets:
            self.revert_target(target)

    def add_result(self, value):
        Operation.memory_handler.put_value(value, True)

    def is_ready(self):
        return super(CallOperation, self).is_ready() or 'return' in self.mapping
