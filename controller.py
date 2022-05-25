from operations import ComplexOperation, WhileOperation, ForOperation, IfThenElseOperation, CallOperation, \
    ComputingOperation, ReturnException, BackwardException, Operation, CallException


class Controller:

    def __init__(self, debugger):
        self.debugger = debugger

    def set_next(self, operation):
        operation.index[-1] += 1
        if isinstance(operation, CallOperation):
            operation.set_operation(operation.get_current_to_evaluate())
        operation.get_current_to_evaluate().initialize()
        if operation.get_current_to_evaluate().is_controllable():
            self.debugger.get_call().set_operation(operation.get_current_to_evaluate())

    def next_operation_complex(self, operation: ComplexOperation, evaluation):
        if evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                self.set_next(operation)
            else:
                operation.parent.next_operation(evaluation)

    def prev_operation_complex(self, operation: ComplexOperation):
        if operation.get_index() > 0:
            operation.index[-1] -= 1
            if isinstance(operation.operations[operation.index[-1]], CallOperation):
                raise CallException(operation.operations[operation.index[-1]])
        else:
            operation.parent.prev_operation()

    def next_operation_computing(self, operation: ComputingOperation, evaluation):
        if evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                self.set_next(operation)

    def prev_operation_computing(self, operation: ComputingOperation):
        while operation.get_index() > 0:
            operation.index[-1] -= 1
            if isinstance(operation.operations[operation.index[-1]], CallOperation):
                raise CallException(operation.operations[operation.index[-1]])
        else:
            operation.parent.prev_operation()

    def next_operation_call(self, operation: CallOperation, evaluation):
        if evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                self.set_next(operation)
            else:
                if operation.name != 'boot':
                    raise ReturnException((True, -1))

    def prev_operation_call(self, operation: CallOperation):
        if operation.get_index() > 0:
            operation.index[-1] -= 1
            if isinstance(operation.operations[operation.index[-1]], CallOperation):
                raise CallException(operation.operations[operation.index[-1]])
        else:
            raise BackwardException
    
    def next_operation_while(self, operation: WhileOperation, evaluation):
        if operation.get_index() == 0 and evaluation[0]:
            if self.debugger.get_value(evaluation[1]):
                self.next_operation_complex(operation, evaluation)
            else:
                operation.parent.next_operation(evaluation)
        elif evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                self.set_next(operation)
            else:
                operation.index[-1] = 0

    def prev_operation_while(self, operation: WhileOperation):
        if operation.get_index() == 1 and operation.number[-1] != 0:
            operation.index[-1] = len(operation.operations) - 1
            operation.number[-1] -= 1
            if isinstance(operation.operations[operation.index[-1]], CallOperation):
                raise CallException(operation.operations[operation.index[-1]])
        elif operation.get_index() == 1 and operation.number[-1] == 0:
            operation.finalize()
            operation.parent.prev_operation()
        else:
            operation.index[-1] -= 1
            if isinstance(operation.operations[operation.index[-1]], CallOperation):
                raise CallException(operation.operations[operation.index[-1]])
    
    def next_operation_for(self, operation: ForOperation, evaluation):
        if operation.get_index() == 0 and evaluation[0]:
            self.set_next(operation)
        elif operation.get_index() == 1 and evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                self.set_next(operation)
            else:
                operation.parent.next_operation(evaluation)
        elif evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                self.set_next(operation)
            else:
                if operation.iter[-1] < len(operation.iterable[-1]):
                    operation.index[-1] = 1
                    if operation.get_current_to_evaluate().is_controllable():
                        self.debugger.get_call().set_operation(operation.get_current_to_evaluate())
                else:
                    operation.parent.next_operation(evaluation)

    def prev_operation_for(self, operation: ForOperation):
        if operation.get_index() == 1 and operation.iter[-1] != 0:
            operation.index[-1] = len(operation.operations) - 1
            operation.iter[-1] -= 1
            Operation.debugger.revert_target(operation.target)
            if isinstance(operation.operations[operation.index[-1]], CallOperation):
                raise CallException(operation.operations[operation.index[-1]])
        if operation.get_index() == 1 and operation.iter[-1] == 0:
            operation.finalize()
            operation.parent.prev_operation()
        else:
            operation.index[-1] -= 1
            if isinstance(operation.operations[operation.index[-1]], CallOperation):
                raise CallException(operation.operations[operation.index[-1]])
    
    def next_operation_if(self, operation: IfThenElseOperation, evaluation):
        if operation.get_index() == 0 and evaluation[0]:
            if self.debugger.get_value(evaluation[1]):
                operation.index[-1] += operation.then_index
                operation.get_current_to_evaluate().initialize()
            else:
                operation.index[-1] += operation.else_index
                operation.get_current_to_evaluate().initialize()
        if evaluation[0]:
            if operation.choices[-1]:
                if operation.index[-1] < operation.else_index:
                    operation.index[-1] += 1
                    operation.get_current_to_evaluate().initialize()
                else:
                    operation.parent.next_operation(evaluation)
            else:
                if operation.get_index() < len(operation.operations) - 1:
                    operation.index[-1] += 1
                    operation.get_current_to_evaluate().initialize()
                else:
                    operation.parent.next_operation(evaluation)

    def prev_operation_if(self, operation: IfThenElseOperation):
        if operation.get_index() == operation.then_index and operation.choices[-1]:
            operation.finalize()
            operation.parent.prev_operation()
        if operation.get_index() == operation.else_index and not operation.choices[-1]:
            operation.finalize()
            operation.parent.prev_operation()
        else:
            operation.index[-1] -= 1
            if isinstance(operation.operations[operation.index[-1]], CallOperation):
                raise CallException(operation.operations[operation.index[-1]])

    def next_operation_break(self, operation):
        if isinstance(operation.parent, ForOperation) or isinstance(operation.parent, WhileOperation):
            operation.parent.parent.next_operation((True, None))
        else:
            self.next_operation_break(operation.parent)
