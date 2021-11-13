import ast


class SourceVisitor(ast.NodeVisitor):

    def __init__(self):
        self.left_operand = 0
        self.right_operand = 0
        self.source = {}
        self.referencePool = {}

    def set_left_operand(self, left_operand):
        self.left_operand = left_operand

    def set_right_operand(self, right_operand):
        self.right_operand = right_operand

    def set_operands(self, left_operand, right_operand):
        self.set_left_operand(left_operand)
        self.set_right_operand(right_operand)

    def visit_Constant(self, node):
        return node.value

    def visit_Name(self, node):
        return self.source[node.id]

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if isinstance(node.value, ast.Constant):
                    self.source[target.id] = node.value.value
                elif isinstance(node.value, ast.BinOp):
                    self.set_operands(self.evaluate_computation(node.value.left),
                                      self.evaluate_computation(node.value.right))
                    self.source[target.id] = self.visit(node.value.op)
                elif isinstance(node.value, ast.List):
                    self.source[target.id] = []
                    for element in node.value.elts:
                        if isinstance(element, ast.Constant):
                            self.source[target.id].append(element.value)
                elif isinstance(node.value, ast.Call):
                    self.source[target.id] = self.visit_Call(node.value)
                if target.id in self.referencePool:
                    self.updateAll(target.id)
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
        evaluation = self.evaluate_computation(node.value)
        result = self.perform_computation(node.target, node.op, evaluation)
        if isinstance(node.target, ast.Name):
            self.source[node.target.id] = result
            self.updateAll(node.target.id)
        if isinstance(node.target, ast.Subscript):
            if isinstance(node.target.slice, ast.Index):
                if isinstance(node.target.value, ast.Name):
                    if isinstance(node.target.slice.value, ast.Constant):
                        self.source[node.target.value.id][node.target.slice.value.value] = result
                    if isinstance(node.target.slice.value, ast.Name):
                        self.source[node.target.value.id][self.visit(node.target.slice.value)] = result
                    self.updateAll(node.target.value.id)
        print(self.source)

    def perform_computation(self, target, op, evaluation):
        if isinstance(target, ast.Name):
            return self.perform_computation(self.source[target.id], op, evaluation)
        if isinstance(target, ast.Subscript):
            if isinstance(target.slice, ast.Index):
                if isinstance(target.value, ast.Name):
                    if isinstance(target.slice.value, ast.Constant):
                        return self.perform_computation(self.source[target.value.id][target.slice.value.value],
                                                        op, evaluation)
                    if isinstance(target.slice.value, ast.Name):
                        return self.perform_computation(self.source[target.value.id][self.visit(target.slice.value)],
                                                        op, evaluation)
        self.set_operands(target, evaluation)
        return self.visit(op)

    def evaluate_computation(self, value):
        if isinstance(value, ast.Constant):
            return value.value
        if isinstance(value, ast.Name):
            return self.source[value.id]
        if isinstance(value, ast.BinOp):
            self.set_operands(self.evaluate_computation(value.left), self.evaluate_computation(value.right))
            return self.visit(value.op)
        if isinstance(value, ast.Subscript):
            if isinstance(value.slice, ast.Index):
                if isinstance(value.value, ast.Name):
                    if isinstance(value.slice.value, ast.Constant):
                        return self.source[value.value.id][value.slice.value.value]
                    if isinstance(value.slice.value, ast.Name):
                        return self.source[value.value.id][self.visit(value.slice.value)]



    def visit_Compare(self, node):
        self.left_operand = self.evaluate_computation(node.left)
        for c in node.comparators:
            if isinstance(c, ast.Constant):
                self.right_operand = c.value
            if isinstance(c, ast.Name):
                self.right_operand = self.source[c.id]
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

    def visit_Expr(self, node):
        if isinstance(node.value, ast.BinOp):
            self.visit_BinOp(node.value)

    def visit_If(self, node):
        if isinstance(node.test, ast.BoolOp):
            if self.visit_BoolOp(node.test):
                for n in node.body:
                    self.visit(n)
            elif node.orelse:
                for n in node.orelse:
                    self.visit(n)

    def visit_BoolOp(self, node):
        if len(node.values) == 2:
            left_operand = self.visit(node.values[0])
            right_operand = self.visit(node.values[1])
        self.set_operands(left_operand, right_operand)
        return self.visit(node.op)

    def visit_And(self, node):
        return self.left_operand and self.right_operand

    def visit_Or(self, node):
        return self.left_operand or self.right_operand

    def visit_While(self, node):
        while self.visit_Compare(node.test):
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
        if isinstance(node.func, ast.Attribute) or (isinstance(node.func, ast.Name) and node.func.id not in self.source):
            return self.visit_Builtin(node)
        ts = self.source
        tempSource = self.buildTempSource(node)
        self.updateReferencePoolFromCall(tempSource)
        computateablesource = {}
        for key in tempSource:
            computateablesource[key] = tempSource[key][0][0]
        self.source = computateablesource
        for statement in ts[node.func.id][1]:
            self.visit(statement)
        for key in tempSource:
            if len(tempSource[key]) == 2:
                if len(tempSource[key][1]) == 2:
                    ts[tempSource[key][1][0]] = self.source[key]
        self.source = ts

    def is_immutable(self, obj):
        return isinstance(obj, tuple) or isinstance(obj, int) or isinstance(obj, float) \
               or isinstance(obj, complex) or isinstance(obj, str) or isinstance(obj, bytes)

    def visit_For(self, node):
        if isinstance(node.iter, ast.Name):
            for i in range(0, len(self.source[node.iter.id])):
                temp = self.source[node.iter.id][i]
                if isinstance(node.target, ast.Name):
                    self.source[node.target.id] = temp
                for n in node.body:
                    self.visit(n)
                    self.source[node.iter.id][i] = self.source[node.target.id]
            self.source.pop(node.target.id)
        if isinstance(node.iter, ast.Call):
            bounds = self.visit_Call(node.iter)
            for j in range(bounds[0], bounds[1]):
                self.source[node.target.id] = j
                for n in node.body:
                    self.visit(n)
            self.source.pop(node.target.id)



    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            self.visit_Call(node.value)

    def visit_Builtin(self, node):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'append':
                self.source[node.func.value.id] = self.visit_append(self.visit(node.func.value), self.visit(node.args[0]))
                self.updateAll(node.func.value.id)
                return self.source[node.func.value.id]
        if isinstance(node.func, ast.Name):
            if node.func.id == 'len':
                return len(self.source[node.args[0].id])
            if node.func.id == 'range':
                return [self.visit(node.args[0]), self.visit(node.args[1])]

    def visit_append(self, array, element):
        return array + [element]

    def buildTempSource(self, node):
        tempSource = {}
        if isinstance(node.args, list):
            for i in range(0, len(node.args)):
                if isinstance(node.args[i], ast.Name):
                    tempArg = node.args[i].id
                node.args[i] = self.visit(node.args[i])
                if self.is_immutable(node.args[i]):
                    tempSource[self.source[node.func.id][0][i]] = [[node.args[i]]]
                else:
                    tempSource[self.source[node.func.id][0][i]] = [[node.args[i]], [tempArg]]
        for j in range(0, len(node.keywords)):
            if isinstance(node.keywords[j].value, ast.Name):
                tempId = node.keywords[j].value.id
            node.keywords[j].value = self.visit(node.keywords[j].value)
            if self.is_immutable(node.keywords[j].value):
                tempSource[node.keywords[j].arg] = [[node.keywords[j].value]]
            else:
                tempSource[node.keywords[j].arg] = [[node.keywords[j].value], [tempId]]
        return tempSource

    def updateAll(self, updated_reference):
        updated_value = self.source[updated_reference]
        for key in self.referencePool:
            if updated_reference in self.referencePool[key]:
                for reference in self.referencePool[key]:
                    if reference is not updated_reference:
                        self.source[reference] = updated_value

    def updateReferencePoolFromCall(self, tempSource):
        references = {}
        for key in tempSource:
            if len(tempSource[key]) == 2:
                if tempSource[key][1][0] not in references:
                    references[tempSource[key][1][0]] = [key]
                else:
                    references[tempSource[key][1][0]].append(key)
        self.referencePool = references


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
