from operations import ComplexOperation, IfThenElseOperation


class Controller():

    def next_operation_complex(operation : ComplexOperation):
        if operation.is_ended():
            if operation.parent:
                operation.parent.next_operation()
        else:
            if operation.get_current_operation().is_ended():
                operation.next_index()

    def prev_operation_complex(operation : ComplexOperation):
        if operation.is_started():
            operation.get_current_operation().finalize()
            if operation.parent:
                operation.parent.prev_operation()
        else:
            if operation.get_current_operation().is_started():
                operation.prev_index()

    def next_operation_computing(operation : ComplexOperation):
        if operation.is_ended():
            if operation.parent:
                operation.parent.next_operation()
        else:
            if operation.get_current_operation().is_ended():
                operation.next_index()

    def prev_operation_computing(operation : ComplexOperation):
        if operation.is_started():
            operation.get_current_operation().finalize()
            if operation.parent:
                operation.parent.prev_operation()
        else:
            if operation.get_current_operation().is_started():
                operation.prev_index()


    def next_operation_if(operation : IfThenElseOperation):
        if operation.is_ended():
            operation.parent.next_operation()
        else:
            if operation.get_index() == 0 and operation.get_current_operation().is_ended():
                operation.initialize() ## operation.tests.append(operation.get_current_operation().get_evaluation())
                if operation.get_test():
                    operation.next_index()
                else:
                    operation.update_index(2)
            if operation.get_current_operation().is_ended():
                operation.parent.next_operation()

    def prev_operation_if(operation : ComplexOperation):
        if operation.is_started():
            operation.parent.prev_operation()
        else:
            if operation.get_index() == 0:
                operation.finalize()
            if operation.get_current_operation().is_started():
                operation.prev_index()

