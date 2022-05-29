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
adu = lambda a: +a
sbu = lambda a: -a
inv = lambda a: ~a


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

    def __init__(self, return_address):
        self.return_address = return_address
        super(ReturnException, self).__init__('Reyturn')


class Operation:

    debugger = None

    def __init__(self):
        self.parent = None

    def get_value(self):
        return None

    def is_mutable(self):
        return False

    def is_controllable(self):
        return False

    def get_current_operation(self):
        return None

    def initialize(self):
        return

    def evaluate(self):
        return

    def revert(self):
        return

    def handle_return(self, evaluation):
        return


class SingleOperation(Operation):

    def __init__(self):
        Operation.__init__(self)

    def get_current_operation(self):
        return self


class ComplexOperation(Operation):

    def __init__(self, operations):
        self.index = []
        self.operations = operations
        Operation.__init__(self)

    def get_index(self):
        return self.index[-1]

    def get_current_operation(self):
        if self.operations:
            return self.operations[self.get_index()]
        else:
            return None

    def initialize(self):
        self.index.append(0)
        if self.operations:
            self.get_current_operation().initialize()

    def finalize(self):
        self.index.pop()
        
    def can_be_finalized(self):
        return self.index[-1] == 0
    
    def evaluate(self):
        return self.get_current_operation().evaluate()

    def revert(self):
        self.get_current_operation().revert()
        if self.can_be_finalized():
            self.finalize()

    def next_operation(self, evaluation):
        Operation.debugger.controller.next_operation_complex(self, evaluation)

    def prev_operation(self):
        Operation.debugger.controller.prev_operation_complex(self)

    def handle_return(self, evaluation):
        self.next_operation(evaluation)


class ComputingOperation(ComplexOperation):

    def __init__(self, operations):
        self.temporary_values = []
        self.result = None
        super(ComputingOperation, self).__init__(operations)

    def get_value(self):
        return self.result

    def is_evaluated(self):
        return len(self.temporary_values) == len(self.operations)

    def add_temp_result(self, temp_result):
        self.temporary_values.append(temp_result)

    def initialize(self):
        self.temporary_values = []
        super(ComputingOperation, self).initialize()

    def evaluate(self):
        while not self.is_evaluated():
            if isinstance(self.get_current_operation(), CallOperation):
                if 'return' in self.get_current_operation().get_source():
                    self.add_temp_result(self.get_current_operation().get_source()['result'])
                    self.next_operation_computing()
                else:
                    raise CallException(self.get_current_operation())
            else:
                self.add_temp_result(self.get_current_operation().evaluate())
                self.next_operation_computing()
        else:
            return self.finish()

    def finish(self):
        return

    def handle_return(self, evaluation):
        self.add_temp_result(evaluation)
        self.next_operation_computing()
        Operation.debugger.execute(1)

    def next_operation_computing(self):
        Operation.debugger.controller.next_operation_computing(self)

    def prev_operation(self):
        Operation.debugger.controller.prev_operation_computing(self)
        
    def revert(self):
        while self.get_index() > 0:
            self.prev_operation()
        else:
            if self.can_be_finalized():
                self.finalize()


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
        Operation.debugger.insert_value(self)
        return Operation.debugger.get_last_allocated()

    def get_value(self):
        return self.value


class NameOperation(SingleOperation):

    def __init__(self, name):
        self.name = name
        SingleOperation.__init__(self)

    def evaluate(self):
        return Operation.debugger.get_reference(self.name)

    def get_value(self):
        Operation.debugger.get_referenced_value(self.name)

    def is_mutable(self):
        return Operation.debugger.is_mutable(Operation.debugger.get_reference(self.name))


class ReturnOperation(ComplexOperation):

    def __init__(self, operations):
        ComplexOperation.__init__(self, operations)

    def evaluate(self):
        if not self.get_current_operation():
            raise ReturnException(-1)
        else:
            result = self.get_current_operation().evaluate()
            raise ReturnException(result)
        
    def finalize(self):
        super(ReturnOperation, self).finalize()
        Operation.debugger.revert_target('return')


class BinaryOperation(ComputingOperation):

    def __init__(self, op, operations):
        self.op = op
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        self.result = self.op(value[0], value[1])
        Operation.debugger.insert_value(self)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()

    def is_mutable(self):
        return Operation.debugger.is_mutable(self.temporary_values[0])


class BooleanOperation(ComputingOperation):

    def __init__(self, op, operations):
        self.op = op
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        self.result = self.op(value[0], value[1])
        Operation.debugger.insert_value(self)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()


class CompareOperation(ComputingOperation):

    def __init__(self, comparisons, operations):
        self.comparisons = comparisons
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        self.result = True
        for i in range(len(self.comparisons)):
            self.result = self.result and self.comparisons[i](value[i], value[i + 1])
        Operation.debugger.insert_value(self)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()


class SubscriptOperation(ComputingOperation):

    def __init__(self, operations):
        ComplexOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        self.result = value[0][value[1]]
        Operation.debugger.insert_value(self)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()

    def is_mutable(self):
        return not Operation.debugger.memory_handler.is_immutable(self.result)


class AugAssignOperation(ComputingOperation):

    def __init__(self, target, operations):
        self.target = target
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        Operation.debugger.update_target(self.target, value[0])
        self.temporary_values = []
        return -1

    def revert(self):
        super(AugAssignOperation, self).revert()
        Operation.debugger.revert_target(self.target)


class AssignOperation(ComputingOperation):

    def __init__(self, targets, operations):
        self.targets = targets
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        Operation.debugger.update_targets(self.targets, value[0])
        self.temporary_values = []
        return -1

    def revert(self):
        super(AssignOperation, self).revert()
        Operation.debugger.revert_targets(self.targets)


class ListOperation(ComputingOperation):

    def __init__(self, operations):
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        self.result = [i for i in value]
        Operation.debugger.insert_value(self)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()

    def is_mutable(self):
        return True


class SetOperation(ComputingOperation):

    def __init__(self, operations):
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        self.result = {i for i in value}
        Operation.debugger.insert_value(self)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()

    def is_mutable(self):
        return True


class DictOperation(ComputingOperation):

    def __init__(self, keys, operations):
        self.keys = keys
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        self.result = {}
        for i in range(len(value)):
            self.result[self.keys[i]] = value[i]
        Operation.debugger.insert_value(self)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()

    def is_mutable(self):
        return True


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

    def can_be_finalized(self):
        return self.number[-1] == 0 and super(WhileOperation, self).can_be_finalized()

    def evaluate(self):
        if self.get_index() == 0:
            evaluation = self.get_current_operation().evaluate()
            if Operation.debugger.get_value(evaluation):
                self.number[-1] += 1
            return evaluation
        else:
            return self.get_current_operation().evaluate()

    def next_operation(self, evaluation):
        Operation.debugger.controller.next_operation_while(self, evaluation)

    def prev_operation(self):
        Operation.debugger.controller.prev_operation_while(self)


class IterOperation(SingleOperation):

    def __init__(self):
        SingleOperation.__init__(self)

    def evaluate(self):
        parent = self.parent
        if parent.iterable[-1]:
            Operation.debugger.update_target(parent.target, parent.iterable[-1][parent.iter[-1]])
            parent.iter[-1] += 1
        return -1

    def revert(self):
        Operation.debugger.revert_target(self.parent.target)


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
        
    def can_be_finalized(self):
        return self.iter[-1] == 0 and super(ForOperation, self).can_be_finalized()

    def evaluate(self):
        if self.get_index() == 0:
            evaluation = self.get_current_operation().evaluate()
            self.iterable.append(Operation.debugger.get_value(evaluation))
            return evaluation
        return self.get_current_operation().evaluate()

    def next_operation(self, evaluation):
        Operation.debugger.controller.next_operation_for(self, evaluation)

    def prev_operation(self):
        Operation.debugger.controller.prev_operation_for(self)


class IfThenElseOperation(ComplexOperation):

    def __init__(self, else_index, operations):
        self.choices = []
        self.then_index = 1
        self.else_index = else_index
        ComplexOperation.__init__(self, operations)

    def is_controllable(self):
        return True
    
    def finalize(self):
        self.choices.pop()
        super(IfThenElseOperation, self).finalize()

    def evaluate(self):
        if self.get_index() == 0:
            evaluation = self.get_current_operation().evaluate()
            self.choices.append(Operation.debugger.get_value(evaluation))
            return evaluation
        return self.get_current_operation().evaluate()

    def next_operation(self, evaluation):
        Operation.debugger.controller.next_operation_if(self, evaluation)

    def prev_operation(self):
        Operation.debugger.controller.prev_operation_if(self)


class AttributeOperation(ComputingOperation):

    def __init__(self, target, attr, operations):
        self.target = target
        self.attr = attr
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        duplicate = copy.deepcopy(Operation.debugger.get_referenced_value(self.target))
        Operation.debugger.update_target(self.target, duplicate)
        self.result = getattr(Operation.debugger.get_referenced_value(self.target), self.attr)(*value)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()

    def finalize(self):
        Operation.debugger.revert_target(self.target)

    def is_mutable(self):
        return not Operation.debugger.memory_handler.is_immutable(self.result)


class SliceOperation(ComputingOperation):

    def __init__(self, operations):
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        self.result = slice(value[0], value[1], value[2])
        Operation.debugger.insert_value(self)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()

    def is_mutable(self):
        return True


class BuiltinOperation(ComputingOperation):

    def __init__(self, attr, operations):
        self.attr = attr
        ComputingOperation.__init__(self, operations)

    def finish(self):
        value = [Operation.debugger.get_value(address) for address in self.temporary_values]
        self.result = getattr(builtins, self.attr)(*value)
        if isinstance(self.result, range):
            self.result = [*self.result]
        Operation.debugger.insert_value(self)
        self.temporary_values = []
        return Operation.debugger.get_last_allocated()

    def is_mutable(self):
        return not Operation.debugger.memory_handler.is_immutable(self.result)


class CallOperation(ComplexOperation):

    def __init__(self, name, args, operations):
        self.name = name
        self.args = args
        self.source = {}
        self.operation = None
        ComplexOperation.__init__(self, operations)

    def is_controllable(self):
        return True

    def evaluate_mapping(self):
        current_argument = self.args[len(self.source)]
        if isinstance(current_argument, CallOperation):
            raise CallException(current_argument)
        if isinstance(current_argument, NameOperation):
            address = Operation.debugger.get_prev_call().get_source()[current_argument.name][-1]
            if Operation.debugger.memory_handler.is_mutable(address):
                addresses = copy.deepcopy(Operation.debugger.get_prev_call().get_source()[current_argument.name])
            else:
                addresses = [address]
        else:
            addresses = [current_argument.evaluate()[1]]
        self.source[Operation.debugger.get_function_args(self.name)[len(self.source)]] = addresses

    def set_return(self, address):
        self.source['return'] = address

    def initialize(self):
        super(CallOperation, self).initialize()
        self.operation = self

    def evaluate(self):
        while len(self.source) < len(self.args):
            self.evaluate_mapping()
        self.set_operation(self.get_current_operation())
        return self.operation.evaluate()

    def revert(self):
        self.get_current_operation().revert()

    def get_source(self):
        return self.source

    def get_operation(self):
        return self.operation

    def set_operation(self, operation):
        self.operation = operation

    def next_operation(self, evaluation):
        Operation.debugger.controller.next_operation_call(self)

    def prev_operation(self):
        Operation.debugger.controller.prev_operation_call(self)
