import builtins
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

    def __init__(self, return_value):
        self.return_value = return_value
        super(ReturnException, self).__init__('Reyturn')


class StartException(Exception):
    
    def __init__(self):
        super(StartException, self).__init__('Start Wars')


class Operation:

    debugger = None

    def __init__(self):
        self.parent = None

    def get_current(self):
        return None

    def evaluate(self):
        return

    def revert(self):
        return

    def get_call(self):
        return Operation.debugger.get_call()


class SingleOperation(Operation):

    def __init__(self):
        Operation.__init__(self)

    def get_current(self):
        return self


class ComplexOperation(Operation):

    def __init__(self, operations):
        self.index = []
        self.operations = operations
        Operation.__init__(self)

    def get_index(self):
        return self.index[-1]

    def get_current(self):
        return self.operations[self.get_index()]

    def initialize(self):
        self.index.append(0)

    def finalize(self):
        self.index.pop()

    def evaluate(self):
        self.get_current().evaluate()

    def finish(self):
        return

    def revert(self):
        self.get_current().revert()

    def next_operation(self):
        Operation.debugger.next_operation_complex(self)

    def prev_operation(self):
        Operation.debugger.prev_operation_complex(self)


class ComputingOperation(ComplexOperation):

    def __init__(self, operations):
        self.temporary_values = []
        super(ComputingOperation, self).__init__(operations)

    def is_evaluated(self):
        return False

    def add_temp_result(self, temp_result):
        self.temporary_values.append(temp_result)

    def initialize(self):
        self.temporary_values = []

    def next_operation(self):
        Operation.debugger.next_operation_computing(self)

    def prev_operation(self):
        Operation.debugger.prev_operation_computing(self)


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
        return True, self.value


class NameOperation(SingleOperation):

    def __init__(self, name):
        self.name = name
        SingleOperation.__init__(self)

    def evaluate(self):
        return True, self.get_call().get_referenced_value(self.name)


class ReturnOperation(ComplexOperation):

    def __init__(self, operations):
        ComplexOperation.__init__(self, operations)

    def evaluate(self):
        if not self.get_current():
            return True, None
        else:
            result = self.get_current().evaluate()
            if result[0]:
                raise ReturnException(result[1])


class BinaryOperation(ComputingOperation):

    def __init__(self, op, operations):
        self.op = op
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == 2

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            result = self.op(self.temporary_values[0], self.temporary_values[1])
            self.temporary_values = []
            return True, result


class BooleanOperation(ComputingOperation):

    def __init__(self, op, operations):
        self.op = op
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == 2

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            result = self.op(self.temporary_values[0], self.temporary_values[1])
            self.temporary_values = []
            return True, result


class CompareOperation(ComputingOperation):

    def __init__(self, comparisons, operations):
        self.comparisons = comparisons
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == len(self.operations)

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            result = True
            for i in range(len(self.comparisons)):
                result = result and self.comparisons[i](self.temporary_values[i], self.temporary_values[i + 1])
            self.temporary_values = []
            return True, result


class SubscriptOperation(ComputingOperation):

    def __init__(self, operations):
        ComplexOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == 2

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            result = self.temporary_values[0][self.temporary_values[1]]
            self.temporary_values = []
            return True, result


class AugAssignOperation(ComputingOperation):

    def __init__(self, target, operations):
        self.target = target
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == 1

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            self.get_call().update_target(self.target, self.temporary_values[0])
            self.temporary_values = []
            self.parent.next_operation()

    def revert_evaluation(self):
        self.get_call().revert_target(self.target)
        self.finalize()
        self.parent.prev_operation()


class AssignOperation(ComputingOperation):

    def __init__(self, targets, operations):
        self.targets = targets
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == 1

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            self.get_call().update_targets(self.targets, self.temporary_values[0])
            self.temporary_values = []
            self.parent.next_operation()

    def revert_evaluation(self):
        self.get_call().revert_targets(self.targets)
        self.finalize()
        self.parent.prev_operation()


class ListOperation(ComputingOperation):

    def __init__(self, operations):
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == len(self.operations)

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            result = [i for i in self.temporary_values]
            self.temporary_values = []
            return True, result


class SetOperation(ComputingOperation):

    def __init__(self, operations):
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == len(self.operations)

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            result = {i for i in self.temporary_values}
            self.temporary_values = []
            return True, result


class DictOperation(ComputingOperation):

    def __init__(self, keys, operations):
        self.keys = keys
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == len(self.operations)

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            result = {}
            for i in self.temporary_values:
                result[self.keys[i]] = self.temporary_values[i]
            self.temporary_values = []
            return True, result


class WhileOperation(ComplexOperation):

    def __init__(self, operations):
        self.number = []
        ComplexOperation.__init__(self, operations)

    def initialize(self):
        self.number.append(0)
        super(WhileOperation, self).initialize()

    def finalize(self):
        self.number.pop()
        super(WhileOperation, self).finalize()

    def evaluate(self):
        if self.get_index() == 0:
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.next_operation()
                self.number[-1] += 1
            elif evaluation[1]:
                self.parent.next_operation()
        else:
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.next_operation()

    def revert_evaluation(self):
        if self.get_index() == 0 and self.number[-1] == 0:
            self.finalize()
            self.parent.prev_operation()
        elif self.get_index() == 0 and self.number[-1] > 0:
            self.number[-1] -= 1
            self.prev_operation()
        else:
            self.get_current().revert()


class ForOperation(ComplexOperation):

    def __init__(self, target, operations):
        self.target = target
        self.iter = []
        self.iterable = []
        ComplexOperation.__init__(self, operations)

    def initialize(self):
        self.iter.append(0)
        super(ForOperation, self).initialize()

    def finalize(self):
        self.iter.pop()
        self.iterable.pop()
        super(ForOperation, self).finalize()

    def evaluate(self):
        if self.get_index() == 0:
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.next_operation()
                self.iterable.append(evaluation[1])
        if self.get_index() == 1:
            self.get_call().update_target(self.target, self.iterable[-1][self.iter[-1]])
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.next_operation()
        else:
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.next_operation()

    def revert_evaluation(self):
        if self.get_index() == 1 and self.iter[-1] == 0:
            self.finalize()
            self.parent.prev_operation()
        elif self.get_index() == 1 and self.iter[-1] > 0:
            self.get_current().revert()
            self.iter[-1] -= 1
            self.get_call().revert_target(self.target)
            self.prev_operation()
        else:
            self.get_current().revert()


class IfThenElseOperation(ComplexOperation):

    def __init__(self, else_index, operations):
        self.choices = []
        self.then_index = 1
        self.else_index = else_index
        ComplexOperation.__init__(self, operations)

    def evaluate(self):
        if self.get_index() == 0:
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.choices.append(evaluation[1])
                self.next_operation()
        else:
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.next_operation()

    def revert_evaluation(self):
        if self.get_index() == 1 and self.choices[-1]:
            self.finalize()
            self.parent.prev_operation()
        if self.get_index() == self.else_index and not self.choices[-1]:
            self.finalize()
            self.parent.prev_operation()
        else:
            self.get_current().revert()


class AttributeOperation(ComputingOperation):

    def __init__(self, target, attr, operations):
        self.target = target
        self.attr = attr
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == len(self.operations)

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            address = Operation.debugger.get_call().mapping[self.target][-1]
            value = self.debugger.memory_handler.reference_values[address][-1]
            result = getattr(value, self.attr)(*self.temporary_values)
            self.temporary_values = []
            return True, result

    def revert_evaluation(self):
        Operation.debugger.get_call().revert_target(self.target)


class SliceOperation(ComputingOperation):

    def __init__(self, operations):
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == 2

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            result = slice(self.temporary_values[0], self.temporary_values[1], self.temporary_values[20])
            self.temporary_values = []
            return True, result
        

class BuiltinOperation(ComputingOperation):

    def __init__(self, attr, operations):
        self.attr = attr
        ComputingOperation.__init__(self, operations)

    def is_evaluated(self):
        return len(self.temporary_values) == len(self.operations)

    def evaluate(self):
        while not self.is_evaluated():
            evaluation = self.get_current().evaluate()
            if evaluation[0]:
                self.add_temp_result(evaluation[1])
                self.next_operation()
        else:
            result = getattr(builtins, self.attr)(*self.temporary_values)
            self.temporary_values = []
            return True, result


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
            key = Operation.source_creator.get_function_args(self.name)[len(self.mapping)]
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
            self.mapping[target] = [Operation.memory_handler.address - 1]
            return
        address = self.mapping[target][-1]
        if Operation.memory_handler.is_mutable(address):
            Operation.memory_handler.reference_values[address].append(value)
        else:
            Operation.memory_handler.put_value(value, False)
            self.mapping[target].append(Operation.memory_handler.address - 1)

    def update_targets(self, targets, value, mutable):
        if len(targets) == 1:
            self.update_target(targets[0], value, mutable)
        else:
            for i in range(len(targets)):
                self.update_target(targets[i], value, mutable)

    def revert_target(self, target):
        address = self.mapping[target][-1]
        if Operation.memory_handler.inv_value(address):
            self.mapping[target].pop()
            if not self.mapping[target]:
                self.mapping.pop(target)

    def revert_targets(self, targets):
        for target in targets:
            self.revert_target(target)

    def add_result(self, value):
        Operation.memory_handler.put_value(value, True)

    def is_ready(self):
        return super(CallOperation, self).is_ready() or 'return' in self.mapping
