from operations import ComplexOperation, WhileOperation, ForOperation, IfThenElseOperation


class Controller:

    def next_operation_complex(self, operation: ComplexOperation, evaluation):
        pass

    def prev_operation_complex(self, operation: ComplexOperation):
        pass
    
    def next_operation_while(self, operation: WhileOperation, evaluation):
        pass

    def prev_operation_while(self, operation: WhileOperation):
        pass
    
    def next_operation_for(self, operation: ForOperation, evaluation):
        pass

    def prev_operation_for(self, operation: ForOperation):
        pass
    
    def next_operation_if(self, operation: IfThenElseOperation, evaluation):
        pass

    def prev_operation_if(self, operation: IfThenElseOperation):
        pass