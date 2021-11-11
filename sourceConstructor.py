import ast


class SourceVisitor(ast.NodeVisitor):

    def __init__(self):
        self.left_operand = 0
        self.right_operand = 0
        self.temp_result = 0
        self.source = {}

    def set_left_operand(self, left_operand):
        self.left_operand = left_operand

    def set_right_operand(self, right_operand):
        self.right_operand = right_operand

    def set_operands(self, left_operand, right_operand):
        self.set_left_operand(left_operand)
        self.set_right_operand(right_operand)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if isinstance(node.value, ast.Constant):
                    self.source[target.id] = node.value.value
                elif isinstance(node.value, ast.BinOp):
                    self.set_operands(self.evaluateComputation(node.value.left),
                                      self.evaluateComputation(node.value.right))
                    self.visit(node.value.op)
                    self.source[target.id] = self.temp_result
                elif isinstance(node.value, ast.List):
                    self.source[target.id] = []
                    for element in node.value.elts:
                        if isinstance(element, ast.Constant):
                            self.source[target.id].append(element.value)
                print(self.source)

    def visit_Add(self, node):
        self.temp_result = self.left_operand + self.right_operand

    def visit_Sub(self, node):
        self.temp_result = self.left_operand - self.right_operand

    def visit_Mult(self, node):
        self.temp_result = self.left_operand * self.right_operand

    def visit_Div(self, node):
        self.temp_result = self.left_operand / self.right_operand

    def visit_AugAssign(self, node):
        evaluation = self.evaluateComputation(node.value)
        self.performComputation(node.target, node.op, evaluation)
        if isinstance(node.target, ast.Name):
            self.source[node.target.id] = self.temp_result
        if isinstance(node.target, ast.Subscript):
            if isinstance(node.target.slice, ast.Index):
                if isinstance(node.target.slice.value, ast.Constant) & isinstance(node.target.value, ast.Name):
                    self.source[node.target.value.id][node.target.slice.value.value] = self.temp_result
        print(self.source)

    def performComputation(self, target, op, evaluation):
        if isinstance(target, ast.Name):
            self.performComputation(self.source[target.id], op, evaluation)
            return
        if isinstance(target, ast.Subscript):
            if isinstance(target.slice, ast.Index):
                if isinstance(target.slice.value, ast.Constant) & isinstance(target.value, ast.Name):
                    self.performComputation(self.source[target.value.id][target.slice.value.value], op, evaluation)
                    return
        self.set_operands(target, evaluation)
        self.visit(op)

    def evaluateComputation(self, value):
        if isinstance(value, ast.Constant):
            return value.value
        if isinstance(value, ast.Name):
            return self.source[value.id]
        if isinstance(value, ast.BinOp):
            self.set_operands(self.evaluateComputation(value.left), self.evaluateComputation(value.right))
            self.visit(value.op)
            return self.temp_result
        if isinstance(value, ast.Subscript):
            if isinstance(value.slice, ast.Index):
                if isinstance(value.slice.value, ast.Constant) & isinstance(value.value, ast.Name):
                    return self.source[value.value.id][value.slice.value.value]

    def visit_Compare(self, node):
        self.left_operand = self.evaluateComputation(node.left)
        for c in node.comparators:
            if isinstance(c, ast.Constant):
                self.right_operand = c.value
        for o in node.ops:
            self.visit(o)

    def visit_GtE(self, node):
        return self.left_operand >= self.right_operand

    def visit_Expr(self, node):
        if isinstance(node.value, ast.BinOp):
            self.visit_BinOp(node.value)

    def visit_If(self, node):
        if isinstance(node.test, ast.BinOp):
            self.visit(node.test)
        if self.temp_result:
            for n in node.body:
                self.visit(n)
        elif node.orelse:
            for n in node.orelse:
                self.visit(n)

    def visit_BinOp(self, node):
        if isinstance(node.left, ast.Compare) & isinstance(node.right, ast.Compare):
            self.set_operands(self.visit_Compare(node.left), self.visit_Compare(node.right))
            self.visit(node.op)

    def visit_While(self, node):
        while self.visit(node.test):
            for n in node.body:
                self.visit(n)
        if node.orelse:
            for n in node.orelse:
                self.visit(n)


def main(source):
    tree = ast.parse(source)
    print(ast.dump(tree))
    usage_analyzer = SourceVisitor()
    usage_analyzer.visit(tree)
    print(usage_analyzer.source)


if __name__ == '__main__':
    text = """a = 2
b = 4
c = a + b
a = a + c
ll = [1, 2, 3, 4]
a += b
a += a * b
a += ll[2]
ll[3] += b
if (a * 2 >= 4) & (1 > a | b > 3):
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
if (a * 2 >= 4) & (1 > a | b > 3):
    for i in range(0, len(ll)):
        ll[i] *= ll[i]
    for i in ll:
        i /= i
    else:
        b += 1
else:
    c = 2
    while c > 0:
        c -= 1
a = 4
b += a"""
    main(text)
