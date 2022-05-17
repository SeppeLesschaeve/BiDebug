import builtins
import copy

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

    def __init__(self, name):
        self.name = name
        super(CallException, self).__init__('Callrisian')


class ReturnException(Exception):

    def __init__(self, return_value):
        self.return_value = return_value
        super(ReturnException, self).__init__('Reyturn')


class StartException(Exception):
    
    def __init__(self):
        super(StartException, self).__init__('Start Wars')


class Operation:

    def __init__(self):
        self.parent = None

    def is_controllable(self):
        return False

    def get_current_to_evaluate(self):
        return None

    def get_current_to_revert(self):
        return None

    def initialize(self):
        return

    def evaluate(self, debugger):
        return

    def revert(self, debugger):
        return


class SingleOperation(Operation):

    def __init__(self):
        Operation.__init__(self)

    def get_current_to_evaluate(self):
        return self


class ComplexOperation(Operation):

    def __init__(self, operations):
        self.index = []
        self.operations = operations
        Operation.__init__(self)

    def get_index(self):
        return self.index[-1]

    def get_current_to_evaluate(self):
        return self.operations[self.get_index()]

    def get_current_to_revert(self):
        return self.operations[self.get_index()]

    def initialize(self):
        self.index.append(0)
        self.get_current_to_evaluate().initialize()

    def finalize(self):
        self.index.pop()

    def evaluate(self, debugger):
        return self.get_current_to_evaluate().evaluate(debugger)

    def revert(self, debugger):
        self.get_current_to_evaluate().revert(debugger)

    def next_operation(self, controller, evaluation):
        controller.next_operation_complex(self, evaluation)

    def prev_operation(self, controller):
        controller.prev_operation_complex(self)


class ComputingOperation(ComplexOperation):

    def __init__(self, operations):
        self.temporary_values = []
        super(ComputingOperation, self).__init__(operations)

    def is_evaluated(self):
        return len(self.temporary_values) == len(self.operations)

    def add_temp_result(self, temp_result):
        self.temporary_values.append(temp_result)

    def initialize(self):
        self.temporary_values = []
        super(ComputingOperation, self).initialize()

    def evaluate(self, debugger):
        while not self.is_evaluated():
            if isinstance(self.get_current_to_evaluate(), CallOperation):
                raise CallException(self.get_current_to_evaluate().name)
            evaluation = self.get_current_to_evaluate().evaluate(debugger)
            self.add_temp_result(evaluation[1])
            self.next_operation_computing(debugger.controller, evaluation)
        else:
            return self.finish(debugger)

    def finish(self, debugger):
        return

    def next_operation_computing(self, controller, evaluation):
        controller.next_operation_computing(self, evaluation)

    def prev_operation(self, controller):
        controller.prev_operation_computing(self)


class BreakOperation(SingleOperation):

    def __init__(self):
        SingleOperation.__init__(self)

    def evaluate(self, debugger):
        raise BreakException

    def get_current_to_revert(self):
        return self


class ConstantOperation(SingleOperation):

    def __init__(self, value):
        self.value = value
        SingleOperation.__init__(self)

    def evaluate(self, debugger):
        return True, self.value


class NameOperation(SingleOperation):

    def __init__(self, name):
        self.name = name
        SingleOperation.__init__(self)

    def evaluate(self, debugger):
        return True, debugger.get_referenced_value(self.name)


class ReturnOperation(ComplexOperation):

    def __init__(self, operations):
        ComplexOperation.__init__(self, operations)

    def evaluate(self, debugger):
        if not self.get_current_to_evaluate():
            raise ReturnException(None)
        else:
            result = self.get_current_to_evaluate().evaluate(debugger)
            if result[0]:
                raise ReturnException(result[1])

    def get_current_to_revert(self):
        return self


class BinaryOperation(ComputingOperation):

    def __init__(self, op, operations):
        self.op = op
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        result = self.op(self.temporary_values[0], self.temporary_values[1])
        self.temporary_values = []
        return True, result


class BooleanOperation(ComputingOperation):

    def __init__(self, op, operations):
        self.op = op
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        result = self.op(self.temporary_values[0], self.temporary_values[1])
        self.temporary_values = []
        return True, result


class CompareOperation(ComputingOperation):

    def __init__(self, comparisons, operations):
        self.comparisons = comparisons
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        result = True
        for i in range(len(self.comparisons)):
            result = result and self.comparisons[i](self.temporary_values[i], self.temporary_values[i + 1])
        self.temporary_values = []
        return True, result


class SubscriptOperation(ComputingOperation):

    def __init__(self, operations):
        ComplexOperation.__init__(self, operations)

    def finish(self, debugger):
        result = self.temporary_values[0][self.temporary_values[1]]
        self.temporary_values = []
        return True, result


class AugAssignOperation(ComputingOperation):

    def __init__(self, target, operations):
        self.target = target
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        debugger.update_target(self.target, self.temporary_values[0])
        self.temporary_values = []
        return True, None

    def revert(self, debugger):
        debugger.revert_target(self.target)
        self.finalize()

    def get_current_to_revert(self):
        return self


class AssignOperation(ComputingOperation):

    def __init__(self, targets, operations):
        self.targets = targets
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        debugger.update_targets(self.targets, self.temporary_values[0])
        self.temporary_values = []
        return True, None

    def revert(self, debugger):
        debugger.revert_targets(self.targets)
        self.finalize()

    def get_current_to_revert(self):
        return self


class ListOperation(ComputingOperation):

    def __init__(self, operations):
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        result = [i for i in self.temporary_values]
        self.temporary_values = []
        return True, result


class SetOperation(ComputingOperation):

    def __init__(self, operations):
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        result = {i for i in self.temporary_values}
        self.temporary_values = []
        return True, result


class DictOperation(ComputingOperation):

    def __init__(self, keys, operations):
        self.keys = keys
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        result = {}
        for i in self.temporary_values:
            result[self.keys[i]] = self.temporary_values[i]
        self.temporary_values = []
        return True, result


class WhileOperation(ComplexOperation):

    def __init__(self, operations):
        self.number = []
        ComplexOperation.__init__(self, operations)

    def is_controllable(self):
        return True

    def initialize(self):
        self.number.append(0)
        super(WhileOperation, self).initialize()

    def finalize(self):
        self.number.pop()
        super(WhileOperation, self).finalize()

    def evaluate(self, debugger):
        if self.get_index() == 0:
            evaluation = self.get_current_to_evaluate().evaluate(debugger)
            if evaluation[0]:
                self.number[-1] += 1
            return evaluation
        else:
            return self.get_current_to_evaluate().evaluate(debugger)

    def revert(self, debugger):
        self.get_current_to_revert().revert(debugger)
        if self.get_index() == 1 and self.number[-1] == 0:
            self.finalize()
        elif self.get_index() == 1 and self.number[-1] > 0:
            self.number[-1] -= 1

    def next_operation(self, controller, evaluation):
        controller.next_operation_while(self, evaluation)

    def prev_operation(self, controller):
        controller.prev_operation_while(self)


class ForOperation(ComplexOperation):

    def __init__(self, target, operations):
        self.target = target
        self.iter = []
        self.iterable = []
        ComplexOperation.__init__(self, operations)

    def is_controllable(self):
        return True

    def initialize(self):
        self.iter.append(0)
        super(ForOperation, self).initialize()

    def finalize(self):
        self.iter.pop()
        self.iterable.pop()
        super(ForOperation, self).finalize()

    def evaluate(self, debugger):
        if self.get_index() == 0:
            evaluation = self.get_current_to_evaluate().evaluate(debugger)
            if evaluation[0]:
                self.iterable.append(evaluation[1])
            return evaluation
        elif self.get_index() == 1:
            if self.iterable[-1]:
                debugger.update_target(self.target, self.iterable[-1][self.iter[-1]])
                self.iter[-1] += 1
        return self.get_current_to_evaluate().evaluate(debugger)

    def revert(self, debugger):
        if not (self.get_index() == 1 and self.iter[-1] == 0):
            self.get_current_to_revert().revert(debugger)
        if self.get_index() == 1 and self.iter[-1] == 0:
            self.finalize()
        elif self.get_index() == 1 and self.iter[-1] > 0:
            self.iter[-1] -= 1
            debugger.revert_target(self.target)

    def next_operation(self, controller, evaluation):
        controller.next_operation_for(self, evaluation)

    def prev_operation(self, controller):
        controller.prev_operation_for(self)


class IfThenElseOperation(ComplexOperation):

    def __init__(self, else_index, operations):
        self.choices = []
        self.then_index = 1
        self.else_index = else_index
        ComplexOperation.__init__(self, operations)

    def is_controllable(self):
        return True

    def evaluate(self, debugger):
        if self.get_index() == 0:
            evaluation = self.get_current_to_evaluate().evaluate(debugger)
            if evaluation[0]:
                self.choices.append(evaluation[1])
            return evaluation
        return self.get_current_to_evaluate().evaluate(debugger)

    def revert(self, debugger):
        self.get_current_to_revert().revert(debugger)
        if self.get_index() == self.then_index and self.choices[-1]:
            self.finalize()
        if self.get_index() == self.else_index and not self.choices[-1]:
            self.finalize()

    def next_operation(self, controller, evaluation):
        controller.next_operation_if(self, evaluation)

    def prev_operation(self, controller):
        controller.prev_operation_if(self)


class AttributeOperation(ComputingOperation):

    def __init__(self, target, attr, operations):
        self.target = target
        self.attr = attr
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        value = debugger.get_referenced_value(self.target)
        result = getattr(value, self.attr)(*self.temporary_values)
        self.temporary_values = []
        return True, result

    def revert(self, debugger):
        debugger.revert_target(self.target)

    def get_current_to_revert(self):
        return self


class SliceOperation(ComputingOperation):

    def __init__(self, operations):
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        result = slice(self.temporary_values[0], self.temporary_values[1], self.temporary_values[2])
        self.temporary_values = []
        return True, result
        

class BuiltinOperation(ComputingOperation):

    def __init__(self, attr, operations):
        self.attr = attr
        ComputingOperation.__init__(self, operations)

    def finish(self, debugger):
        result = getattr(builtins, self.attr)(*self.temporary_values)
        if isinstance(result, range):
            result = [*result]
        self.temporary_values = []
        return True, result


class CallOperation(ComplexOperation):

    def __init__(self, name, args, operations):
        self.name = name
        self.args = args
        self.source = {}
        self.operation = None
        ComplexOperation.__init__(self, operations)

    def is_controllable(self):
        return True

    def evaluate_mapping(self, debugger):
        evaluation = self.args[len(self.source)].evaluate(debugger)
        if evaluation[0]:
            if isinstance(self.args[len(self.source)], NameOperation):
                address = debugger.get_prev_call().mapping[self.args[len(self.source)].name][-1]
                if debugger.memory_handler.is_mutable(address):
                    value = copy.deepcopy(debugger.memory_handler.reference_values[address])
                else:
                    value = [debugger.memory_handler.reference_values[address][-1]]
            else:
                if isinstance(self.args[len(self.source)], ConstantOperation):
                    debugger.memory_handler.put_value_typed(evaluation[1], False)
                else:
                    debugger.memory_handler.put_value_typed(evaluation[1], True)
                value = [debugger.memory_handler.address - 1]
            key = debugger.get_function_args(self.name)[len(self.source)]
            self.source[key] = value

    def initialize(self):
        super(CallOperation, self).initialize()
        self.operation = self

    def evaluate(self, debugger):
        while len(self.source) < len(self.args):
            self.evaluate_mapping(debugger)
        self.set_operation(self.get_current_to_evaluate())
        self.operation.evaluate(debugger)

    def get_source(self):
        return self.source

    def set_operation(self, operation):
        self.operation = operation

    def next_operation(self, controller, evaluation):
        controller.next_operation_call(self, evaluation)

    def prev_operation(self, controller):
        controller.prev_operation_call(self)
