from operations import ComplexOperation, WhileOperation, ForOperation, IfThenElseOperation, CallOperation, \
    ReturnException, BackwardException


class Controller:

    def next_operation_complex(self, operation: ComplexOperation, evaluation):
        if evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                operation.index[-1] += 1
            else:
                operation.parent.next_operation(self, evaluation)

    def prev_operation_complex(self, operation: ComplexOperation):
        if operation.get_index() > 0:
            operation.index[-1] -= 1
        else:
            if not operation.parent:
                raise BackwardException
            else:
                operation.parent.prev_operation(self)

    def next_operation_call(self, operation: CallOperation, evaluation):
        if evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                operation.index[-1] += 1
            else:
                raise ReturnException(None)

    def prev_operation_call(self, operation: CallOperation):
        if operation.get_index() > 0:
            operation.index[-1] -= 1
        else:
            raise BackwardException
    
    def next_operation_while(self, operation: WhileOperation, evaluation):
        if operation.get_index() == 0 and evaluation[0]:
            if evaluation[1]:
                self.next_operation_complex(operation, evaluation)
            else:
                operation.parent.next_operation(evaluation)
        if evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                operation.index[-1] += 1
            else:
                operation.index[-1] = 0

    def prev_operation_while(self, operation: WhileOperation):
        if operation.get_index() == 1 and operation.number[-1] != 0:
            operation.index[-1] = len(operation.operations) - 1
        if operation.get_index() == 1 and operation.number[-1] == 0:
            operation.parent.prev_operation(self)
        else:
            operation.index[-1] -= 1
    
    def next_operation_for(self, operation: ForOperation, evaluation):
        if operation.get_index() == 0 and evaluation[0]:
            operation.index[-1] += 1
        if operation.get_index() == 1 and evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1 \
                    and operation.iter[-1] < len(operation.iterable[-1]):
                operation.index[-1] += 1
            else:
                operation.parent.next_operation(evaluation)
        if evaluation[0]:
            if operation.get_index() < len(operation.operations) - 1:
                operation.index[-1] += 1
            else:
                operation.index[-1] = 1

    def prev_operation_for(self, operation: ForOperation):
        if operation.get_index() == 1 and operation.iter[-1] != 0:
            operation.index[-1] = len(operation.operations) - 1
        if operation.get_index() == 1 and operation.iter[-1] == 0:
            operation.parent.prev_operation(self)
        else:
            operation.index[-1] -= 1
    
    def next_operation_if(self, operation: IfThenElseOperation, evaluation):
        if operation.get_index() == 0 and evaluation[0]:
            if evaluation[1]:
                operation.index[-1] += operation.then_index
            else:
                operation.index[-1] += operation.else_index
        if evaluation[0]:
            if operation.choices[-1]:
                if operation.index[-1] < operation.else_index:
                    operation.index[-1] += 1
                else:
                    operation.parent.next_operation(evaluation)
            else:
                if operation.get_index() < len(operation.operations):
                    operation.index[-1] += 1
                else:
                    operation.parent.next_operation(evaluation)

    def prev_operation_if(self, operation: IfThenElseOperation):
        if operation.get_index() == operation.then_index and operation.choices[-1]:
            operation.parent.prev_operation(self)
        if operation.get_index() == operation.else_index and not operation.choices[-1]:
            operation.parent.prev_operation(self)
        else:
            operation.index[-1] -= 1

    def next_operation_break(self, operation):
        if isinstance(operation.parent, ForOperation) or isinstance(operation.parent, WhileOperation):
            operation.parent.parent.next_operation((True, None))
        else:
            self.next_operation_break(operation.parent)
