from typing import Iterable
from sourceConstructor import SourceVisitor
import ast

class ControlFlowHandler:

    counter = 0
    breakpoints = {}

    def __init__(self,program,breakpoints={}):
        self.program = program
        self.astree = ast.parse(program)
        self.usage_analyzer = SourceVisitor()
        self.breakpoints = breakpoints
        self.stepping = False

    def flowFor(self,node: ast.For):
        if node in self.breakpoints:
            self.wait()
        #Daarna zetten we de env op voor de loop

    #simpele definitie call/cc
    def call_cc(f,cc):
        def g(x):
            cc(x)
        return f(g,cc)
    
    #Ik denk dat we een controlestructuur zoals hieronder moeten gebruiken
    def wait(self):
        while (inp := input().lower()):
            if inp == "c":
                self.stepping = False
                return
            if inp == "e":
                exit()
            if inp == "n":
                self.stepping = True
                return
            if inp == "s":
                print(self.usage_analyzer.source)
            elif inp == "f":
                print(self.usage_analyzer.funcs)
            elif inp == "g":
                print(self.usage_analyzer.globals)


    #Hier moeten we continuation passing implementeren (dit loopt maar gewoon over een rij statements en behandelt loops e.d. niet correct!)
    def recVisit(self,node,l):
        if node in self.breakpoints or self.stepping:
            self.wait()
        if getattr(node,"body",None):
            self.recVisit(node.iter,l)
            self.recVisit(node.body,l)
            if getattr(node,"orelse",None):
                self.recVisit(node.orelse,l)
        elif isinstance(node,Iterable):
            for i in node:
                self.recVisit(i,l)
        else:
            l.append(self.usage_analyzer.visit(node))
            print(l)

    def treeify(program):
        return Tree(program)

    def f(self,node):
        currentNode = iter(self.breakpoints)
        while currentNode not in self.breakpoints:

s = """
if a > 0:
    b += 1
else:
    b -= 1
"""
tree = ast.parse(s)
print(ast.dump(tree))
l = []
cfh = ControlFlowHandler(s,{tree.body[0]})
for statement in tree.body:
    cfh.recVisit(statement,l)

