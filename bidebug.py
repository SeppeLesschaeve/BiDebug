import sourceConstructor
import ast
from getch import getch

class bidebug:
    def __init__(self,source):
        self.source_constructor = sourceConstructor.SourceVisitor(self)
        self.states = [{}]
        self.events = []
        self.statements = [statement for statement in source.split("\n") if "=" in statement and "==" not in statement or "append" in statement]
        self.index = 0
        tree = ast.parse(source)
        self.source_constructor.visit(tree)

    def add_state(self,state):
        self.states.append(state)

    def advance(self):
        if self.index < len(self.states) - 1:
            self.index += 1
    
    def revert(self):
        if self.index > 0:
            self.index -= 1
    
    def get_current_state(self):
        return self.states[self.index]
    
def main(program):
    debugger = bidebug(program)
    response = 0
    while response != "3":
        response = getch()
        if response == "1":
            debugger.advance()
            print(debugger.get_current_state())
        elif response == "2":
            debugger.revert()
            print(debugger.get_current_state())
        elif response == "3":
            return
        else:
            print("commands:\n\t1 to advance\n\t2 to revert\n\t3 to quit")

if __name__ == '__main__':
    file_name = "test_2.py"
    f = open(file_name)
    program = ""
    for line in f.readlines():
        program += line
    main(program)
