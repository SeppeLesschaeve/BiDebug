import ast


class SimpleInterpreter(ast.NodeVisitor):



    """Constructor"""
    def __init__(self,source={}):
        self.source = source
        self.referencePool = {}
        self.returnValue = None

    def unpack(self,v):
        """Unpacks a variable such that the return value is its actual value, not its name."""
        if isinstance(v,ast.Name):
            if v.id in self.source:
                return self.source[self.visit(v)]
        elif isinstance(v,ast.Slice):
            step = getattr(v,"step",None)
            if not step:
                step = 1
            else:
                step = self.visit(step)
            return slice(self.visit(v.lower),self.visit(v.upper),step)
        return self.visit(v)

    def visit_Constant(self, node):
        """Returns the value contained by the node."""
        return node.value

    def visit_Name(self, node):
        """Returns the name of the variable contained by the node."""
        return node.id
    
    def visit_Add(self, node):
        """Returns a binary addition function."""
        return lambda x, y: x + y
    
    def visit_Assign(self, node):
        """
        Updates source such that the new state reflects the assignments made by the node.
        Keyword arguments:
            node -- An Assignment node, containing the two relevant fields:
                targets -- a collection of all target variables of the assignment
                value   -- a value that must be assigned to the given targets
        """
        for target in node.targets:
            visitedTarget = self.visit(target)
            if isinstance(target,ast.Tuple):
                if not isinstance(node.value,ast.Tuple):
                    raise TypeError("Cannot unpack non-iterable %s object"%str(type(node.value)))
                visitedValue = self.unpack(node.value)
                if not len(visitedTarget) == len(visitedValue):
                    raise ValueError("Not enough values to unpack (expected %d, got %d)"%(len(visitedTarget),len(visitedValue)))
                for i in range(len(visitedTarget)):
                    self.source[visitedTarget[i]] = visitedValue[i]
            else:
                self.source[self.visit(target)] = self.unpack(node.value)
            self.printSource()
    
    def visit_BinOp(self, node):
        """Visits the binary operation contained by the node."""
        lefthand = self.unpack(node.left)
        righthand = self.unpack(node.right)
        f = self.visit(node.op)
        op = node.op
        return f(lefthand,righthand)

    def printSource(self):
        pSource = {}
        for entry in self.source:
            pSource[entry] = self.source[entry]
        print(pSource)

def main():
    source = ast.parse(
        """
a = 1
a = a + 1
        """
    )
    #print(ast.dump(tree))
    tree = SimpleInterpreter()
    tree.visit(source)
    print(tree)
    #print(usage_analyzer.source)
main()