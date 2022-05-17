import copy

from operations import Operation, CallOperation, BreakException, CallException, ReturnException, BackwardException
from controller import Controller
from program_builder import ProgramBuilder
from util import MemoryHandler


class StopException(Exception):

    def __init__(self):
        super(StopException, self).__init__('Stopa Fett')


class Debugger:

    def __init__(self, text):
        self.program_builder = ProgramBuilder(text)
        self.controller = Controller()
        self.memory_handler = MemoryHandler()
        self.call_stack = []
        self.index = -1
        self.insert('boot')
        Operation.debugger = self

    def get_call(self):
        return self.call_stack[self.index]

    def get_prev_call(self):
        return self.call_stack[self.index - 1]

    def go_back(self):
        self.index -= 1

    def get_function_args(self, name):
        return self.program_builder.get_function_args(name)

    def get_function_operations(self, name):
        return self.program_builder.get_function_operations(name)

    def get_referenced_value(self, name):
        return self.memory_handler.get_value(self.get_call().get_source()[name][-1])

    def update_target(self, target, value):
        self.memory_handler.update_target(target, value, self.get_call().get_source())

    def update_targets(self, targets, value):
        for target in targets:
            self.update_target(target, value)

    def revert_target(self, target):
        self.memory_handler.revert_target(target, self.get_call().get_source())

    def revert_targets(self, targets):
        for target in targets:
            self.revert_target(target)

    def add_result(self, value):
        self.memory_handler.put_value_typed(value, True)

    def insert(self, name):
        self.index += 1
        copy_of_operations = copy.deepcopy(self.program_builder.get_function_operations(name))
        call_operation = CallOperation(name, self.program_builder.get_function_args(name), copy_of_operations)
        for operation in call_operation.operations:
            operation.parent = call_operation
        self.call_stack.insert(self.index, call_operation)
        call_operation.initialize()

    def get_active_source(self, reference):
        source = self.get_call().get_source()
        if reference in source:
            key = source[reference][-1]
            return self.memory_handler.get_value(key)
        else:
            source = self.call_stack[0].get_source()
            if reference in source:
                key = source[reference][-1]
                return self.memory_handler.get_value(key)
            else:
                raise Exception

    def pop(self):
        self.call_stack.pop(self.index)
        self.index -= 1

    def execute(self):
        number = int(input())
        if number == 1:
            try:
                evaluation = self.execute_forward()
                self.get_call().get_current_to_evaluate().next_operation(self.controller, evaluation)
            except CallException as c:
                self.insert(c.name)
            except BreakException:
                self.controller.next_operation_break(self.get_call().get_current_to_evaluate)
            except ReturnException as r:
                self.update_target('return', r.return_value)
        elif number == 2:
            while True:
                try:
                    self.get_call().get_current_to_revert().prev_operation(self.controller)
                    self.execute_backward()
                    break
                except BackwardException:
                    self.pop()
        elif number == 3:
            raise StopException

    def execute_forward(self):
        return self.get_call().get_current_to_evaluate().evaluate(self)

    def execute_backward(self):
        self.get_call().get_current_to_revert().revert()


def main(source_program):
    debugger = Debugger(source_program)
    while True:
        try:
            debugger.execute()
            for key, value in debugger.get_call().mapping.items():
                value = debugger.memory_handler.get_value(value[-1])
                print(key, ' : ', value)
        except StopException:
            break


if __name__ == '__main__':
    file_name = "test_2.py"
    f = open(file_name)
    program = ""
    for line in f.readlines():
        program += line
    main(program)