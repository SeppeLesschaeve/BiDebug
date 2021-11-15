import ast
import builtins


class SourceVisitor(ast.NodeVisitor):

    def __init__(self):
        self.left_operand = 0
        self.right_operand = 0
        self.source = {}
        self.referencePool = {}

    def set_left_operand(self, left_operand):
        if left_operand in self.source:
            self.left_operand = self.source[left_operand]
        else:
            self.left_operand = left_operand

    def set_right_operand(self, right_operand):
        if right_operand in self.source:
            self.right_operand = self.source[right_operand]
        else:
            self.right_operand = right_operand

    def set_operands(self, left_operand, right_operand):
        self.set_left_operand(left_operand)
        self.set_right_operand(right_operand)

    def visit_Constant(self, node):
        return node.value

    def visit_Name(self, node):
        return node.id

    def visit_Assign(self, node):
        for target in node.targets:
            self.source[self.visit(target)] = self.visit(node.value)
            self.updateAll(self.visit(target))
            print(self.source)

    def visit_Add(self, node):
        return self.left_operand + self.right_operand

    def visit_Sub(self, node):
        return self.left_operand - self.right_operand

    def visit_Mult(self, node):
        return self.left_operand * self.right_operand

    def visit_Div(self, node):
        return self.left_operand / self.right_operand

    def visit_AugAssign(self, node):
        self.set_operands(self.visit(node.target), self.visit(node.value))
        if self.visit(node.target) in self.source:
            self.source[self.visit(node.target)] = self.visit(node.op)
            self.updateAll(self.visit(node.target))
        elif isinstance(node.target, ast.Subscript):
            self.source[self.visit(node.target.value)][self.visit(node.target.slice)] = self.visit(node.op)
            self.updateAll(self.visit(node.target.value))
        print(self.source)

    def visit_Subscript(self, node):
        return self.source[self.visit(node.value)][self.visit(node.slice)]

    def visit_Index(self, node):
        return self.source[self.visit(node.value)]

    def visit_Compare(self, node):
        self.set_left_operand(self.visit(node.left))
        for c in node.comparators:
            self.set_right_operand(self.visit(c))
        for o in node.ops:
            return self.visit(o)

    def visit_Eq(self, node):
        return self.left_operand == self.right_operand

    def visit_NotEq(self, node):
        return self.left_operand != self.right_operand

    def visit_Lt(self, node):
        return self.left_operand < self.right_operand

    def visit_LtE(self, node):
        return self.left_operand <= self.right_operand

    def visit_Gt(self, node):
        return self.left_operand > self.right_operand

    def visit_GtE(self, node):
        return self.left_operand >= self.right_operand

    def visit_List(self, node):
        elements = []
        for element in node.elts:
            elements.append(self.visit(element))
        return elements

    def visit_In(self, node):
        return self.left_operand in self.right_operand

    def visit_NotIn(self, node):
        return self.left_operand not in self.right_operand

    def visit_IsNot(self, node):
        return self.left_operand is not self.right_operand

    def visit_Is(self, node):
        return self.left_operand is self.right_operand

    def visit_Expr(self, node):
        self.visit(node.value)

    def visit_BinOp(self, node):
        self.set_operands(self.visit(node.left), self.visit(node.right))
        return self.visit(node.op)

    def visit_If(self, node):
        if self.visit(node.test):
            for n in node.body:
                self.visit(n)
        elif node.orelse:
            for n in node.orelse:
                self.visit(n)

    def visit_BoolOp(self, node):
        if len(node.values) == 2:
            self.set_operands(self.visit(node.values[0]), self.visit(node.values[1]))
            return self.visit(node.op)

    def visit_And(self, node):
        return self.left_operand and self.right_operand

    def visit_Or(self, node):
        return self.left_operand or self.right_operand

    def visit_While(self, node):
        while self.visit(node.test):
            for n in node.body:
                self.visit(n)

    def visit_FunctionDef(self, node):
        self.source[node.name] = []
        arguments = []
        if isinstance(node.args.args, list):
            for argument in node.args.args:
                if isinstance(argument, ast.arg):
                    arguments.append(argument.arg)
        self.source[node.name].append(arguments)
        self.source[node.name].append(node.body)

    def visit_Call(self, node):
        if self.isBuiltin(node):
            return self.visit_Builtin(node)
        ts = self.source
        self.updateReferencePoolFromCall(node)
        self.source = self.buildTempSource(node)
        for statement in ts[node.func.id][1]:
            self.visit(statement)
        for key in self.referencePool:
            ts[key] = self.source[self.referencePool[key][0]]
        self.source = ts

    def is_immutable(self, obj):
        return isinstance(obj, tuple) or isinstance(obj, int) or isinstance(obj, float) \
               or isinstance(obj, complex) or isinstance(obj, str) or isinstance(obj, bytes)

    def visit_For(self, node):
        if isinstance(node.iter, ast.Name):
            listLabel = self.visit(node.iter)
            for i in range(0, len(self.source[listLabel])):
                temp = self.source[listLabel][i]
                self.source[self.visit(node.target)] = temp
                for n in node.body:
                    self.visit(n)
                    self.source[listLabel][i] = self.source[self.visit(node.target)]
        if isinstance(node.iter, ast.Call):
            for j in self.visit(node.iter):
                self.source[node.target.id] = j
                for n in node.body:
                    self.visit(n)
        self.source.pop(node.target.id)

    def visit_Expr(self, node):
        self.visit(node.value)

    def visit_Builtin(self, node):
        arguments = []
        for arg in node.args:
            if self.visit(arg) in self.source:
                arguments.append(self.source[self.visit(arg)])
            else:
                arguments.append(self.visit(arg))
        if isinstance(node.func, ast.Attribute):
            getattr(self.source[self.visit(node.func.value)], node.func.attr)(*arguments)
        if isinstance(node.func, ast.Name):
            return getattr(builtins, node.func.id)(*arguments)

    def buildTempSource(self, node):
        tempSource = {}
        if isinstance(node.args, list):
            for i in range(0, len(node.args)):
                if self.visit(node.args[i]) in self.source:
                    tempSource[self.source[node.func.id][0][i]] = self.source[self.visit(node.args[i])]
                else:
                    tempSource[self.source[node.func.id][0][i]] = self.visit(node.args[i])
        for j in range(0, len(node.keywords)):
            if self.visit(node.keywords[j].value) in self.source:
                tempSource[node.keywords[j].arg] = self.source[self.visit(node.keywords[j].value)]
            else:
                tempSource[node.keywords[j].arg] = self.visit(node.keywords[j].value)
        return tempSource

    def updateAll(self, updated_reference):
        updated_value = self.source[updated_reference]
        for key in self.referencePool:
            if updated_reference in self.referencePool[key]:
                for reference in self.referencePool[key]:
                    if reference is not updated_reference:
                        self.source[reference] = updated_value

    def updateReferencePoolFromCall(self, node):
        references = {}
        if isinstance(node.args, list):
            for i in range(0, len(node.args)):
                tempArg = self.visit(node.args[i])
                if tempArg in self.source and not self.is_immutable(self.source[tempArg]):
                    if tempArg not in references:
                        references[tempArg] = [self.source[node.func.id][0][i]]
                    else:
                        references[tempArg].append(self.source[node.func.id][0][i])
        for j in range(0, len(node.keywords)):
            tempArg = self.visit(node.keywords[j].value)
            if tempArg in self.source and not self.is_immutable(self.source[tempArg]):
                if tempArg not in references:
                    references[tempArg] = [node.keywords[j].arg]
                else:
                    references[tempArg].append(node.keywords[j].arg)
        self.referencePool = references

    def isBuiltin(self, node):
        return isinstance(node.func, ast.Attribute) \
               or (isinstance(node.func, ast.Name) and node.func.id not in self.source)


def main(source):
    tree = ast.parse(source)
    print(ast.dump(tree))
    usage_analyzer = SourceVisitor()
    usage_analyzer.visit(tree)
    print(usage_analyzer.source)


if __name__ == '__main__':
    text = """def test(a, b, l):
    a.append(1)
    b += 1
    c = 1 + b 
    l.append(c)
    l.pop()
    l.sort()
    if 1 in l:
        l.append(1)
    d = range(0, len(l))
    
    
a = 2
b = 4
ll = [1, 2, 3, 4]
if (a * 2 >= 4) and (1 > a or b > 3):
    c = 2
    while c > 0:
        c -= 1
else:
    for i in range(0, len(ll)):
        ll[i] *= ll[i]
    for i in ll:
        i /= i
    else:
        b += 1
if (a * 2 >= 4) and (1 > a or b > 3):
    for i in range(0, len(ll)):
        ll[i] *= ll[i]
    for i in ll:
        i = 2
    else:
        b += 1
else:
    c = 2
    while c > 0:
        c -= 1
a = 4
b += a
test(ll, l = ll, b = 1)"""
    main(text)
