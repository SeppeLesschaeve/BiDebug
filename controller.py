from operations import ComplexOperation, WhileOperation, ForOperation, IfThenElseOperation


class Controller:

    def next_operation_complex(self, operation: ComplexOperation, evaluation):
        if evaluation[0]:
            if operation.get_index() < len(operation.operations):
                operation.index[-1] += 1
            else:
                operation.parent.next_operation(self, evaluation)

    def prev_operation_complex(self, operation: ComplexOperation):
        pass
    
    def next_operation_while(self, operation: WhileOperation, evaluation):
        if operation.get_index() == 0 and evaluation[0]:
            if evaluation[1]:
                if operation.get_index() < len(operation.operations):
                    operation.index[-1] += 1
                else:
                    operation.parent.next_operation(evaluation)
            else:
                operation.parent.next_operation(evaluation)
        if evaluation[0]:
            if operation.get_index() < len(operation.operations):
                operation.index[-1] += 1
            else:
                operation.index[-1] = 0

    def prev_operation_while(self, operation: WhileOperation):
        pass
    
    def next_operation_for(self, operation: ForOperation, evaluation):
        if operation.get_index() == 0 and evaluation[0]:
            operation.index[-1] += 1
        if operation.get_index() == 1 and evaluation[0]:
            if operation.get_index() < len(operation.operations) and operation.iter[-1] < len(operation.iterable[-1]):
                operation.index[-1] += 1
            else:
                operation.parent.next_operation(evaluation)
        if evaluation[0]:
            if operation.get_index() < len(operation.operations):
                operation.index[-1] += 1
            else:
                operation.index[-1] = 1

    def prev_operation_for(self, operation: ForOperation):
        pass
    
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
            if operation.get_index() < len(operation.operations):
                operation.index[-1] += 1
            else:
                operation.parent.next_operation(evaluation)
        if evaluation[0]:
            if operation.get_index() < len(operation.operations):
                operation.index[-1] += 1
            else:
                operation.index[-1] = 0

    def prev_operation_if(self, operation: IfThenElseOperation):
        pass