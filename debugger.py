import copy
from time import perf_counter
import time

from operations import Operation, CallOperation, BreakException, CallException, ReturnException, BackwardException
from controller import Controller, StopException, StartException
from program_builder import ProgramBuilder
from util import MemoryHandler


class EndException(Exception):

    def __init__(self):
        super(EndException, self).__init__('Endor')


class Debugger:

    def __init__(self, text):
        self.program_builder = ProgramBuilder(text)
        self.controller = Controller(self)
        self.memory_handler = MemoryHandler()
        self.call_stack = []
        self.index = 0
        copy_of_operations = copy.deepcopy(self.get_function_operations('boot'))
        call_operation = CallOperation('boot', [], copy_of_operations)
        for operation in call_operation.operations:
            operation.parent = call_operation
        self.call_stack.insert(self.index, call_operation)
        call_operation.initialize()
        Operation.debugger = self

    def get_call(self):
        return self.call_stack[self.index]

    def get_prev_call(self):
        return self.call_stack[self.index - 1]

    def get_function_args(self, name):
        return self.program_builder.get_function_args(name)

    def get_function_operations(self, name):
        return self.program_builder.get_function_operations(name)

    def get_last_allocated(self):
        return self.memory_handler.address - 1

    def is_mutable(self, address):
        return self.memory_handler.is_mutable(address)

    def get_reference(self, name):
        return self.get_active_source(name)[name][-1]

    def insert_value(self, operation):
        self.memory_handler.put_value(operation)

    def get_value(self, address):
        return self.memory_handler.get_value(address)

    def get_referenced_value(self, name):
        return self.memory_handler.get_value(self.get_reference(name))

    def update_target(self, target, value):
        self.memory_handler.update_target(target, value, self.get_active_source(target))

    def add_result(self, target, value):
        self.memory_handler.add_result(target, value, self.get_active_source(target))

    def update_targets(self, targets, value):
        for target in targets:
            self.update_target(target, value)

    def revert_target(self, target):
        self.memory_handler.revert_target(target, self.get_active_source(target))

    def revert_targets(self, targets):
        for target in targets:
            self.revert_target(target)

    def insert(self, operation):
        self.index += 1
        copy_of_operations = copy.deepcopy(self.program_builder.get_function_operations(operation.name))
        call_operation = CallOperation(operation.name, operation.args, copy_of_operations)
        for operation in call_operation.operations:
            operation.parent = call_operation
        self.call_stack.insert(self.index, call_operation)
        call_operation.initialize()

    def get_active_source(self, reference):
        if reference in self.get_call().get_source():
            return self.get_call().get_source()
        else:
            if reference in self.call_stack[0].get_source():
                return self.call_stack[0].get_source()
            else:
                return self.get_call().get_source()

    def pop(self):
        self.call_stack.pop(self.index)
        self.index -= 1

    def go_back(self, evaluation):
        try:
            self.controller.next_operation_call(self.get_call())
        except ReturnException:
            self.index -= 1
            self.get_call().operation.get_current_operation().handle_return(evaluation)

    def call_back(self):
        self.index += 1
        self.execute(2)

    def execute(self, number):
        if number == 1:
            try:
                evaluation = self.execute_forward()
                self.get_call().get_operation().next_operation(evaluation)
            except StopException:
                return
            except CallException as c:
                self.insert(c.operation)
            except BreakException:
                self.controller.next_operation_break(self.get_call().get_current_operation)
            except ReturnException as r:
                self.add_result('return', r.return_address)
                self.go_back(r.return_address)
        elif number == 2:
            try:
                self.get_call().get_operation().prev_operation()
                self.execute_backward()
            except StartException:
                return
            except BackwardException:
                self.pop()
                self.execute_backward()
            except CallException:
                self.call_back()
        elif number == 3:
            raise EndException

    def execute_forward(self):
        if self.get_call().name == 'boot' and self.get_call().get_index() == len(self.get_call().operations):
            raise StopException
        return self.get_call().get_operation().evaluate()

    def execute_backward(self):
        self.get_call().get_operation().revert()


def main(source_program):
    debugger = Debugger(source_program)
    while True:
        try:
            print('new step: ')
            number = int(input())
            debugger.execute(number)
            for key, val in debugger.get_call().get_source().items():
                value = debugger.memory_handler.get_value(val[-1])
                print(key, ' : ', value)
        except EndException:
            break


if __name__ == '__main__':
    file_name = "test_2.py"
    f = open(file_name)
    program = ""
    for line in f.readlines():
        program += line
    main(program)