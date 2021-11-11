import ast


class SourceVisitor(ast.NodeVisitor):

    def __init__(self):
        self.left_operand = 0
        self.right_operand = 0
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
                    self.set_operands(self.evaluate_computation(node.value.left),
                                      self.evaluate_computation(node.value.right))
                    self.source[target.id] = self.visit(node.value.op)
                elif isinstance(node.value, ast.List):
                    self.source[target.id] = []
                    for element in node.value.elts:
                        if isinstance(element, ast.Constant):
                            self.source[target.id].append(element.value)
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
        if isinstance(node.target, ast.Subscript):
            if isinstance(node.target.slice, ast.Index):
                if isinstance(node.target.slice.value, ast.Constant) & isinstance(node.target.value, ast.Name):
                    self.source[node.target.value.id][node.target.slice.value.value] = result
        print(self.source)

    def perform_computation(self, target, op, evaluation):
        if isinstance(target, ast.Name):
            return self.perform_computation(self.source[target.id], op, evaluation)
        if isinstance(target, ast.Subscript):
            if isinstance(target.slice, ast.Index):
                if isinstance(target.slice.value, ast.Constant) & isinstance(target.value, ast.Name):
                    return self.perform_computation(self.source[target.value.id][target.slice.value.value], op, evaluation)
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
                if isinstance(value.slice.value, ast.Constant) & isinstance(value.value, ast.Name):
                    return self.source[value.value.id][value.slice.value.value]

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
            result = self.visit_BoolOp(node.test)
        if result:
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

    def visit_For(self, node):
        k = 2
        if isinstance(node.iter, ast.Name):
            for i in range(0, len(self.source[node.iter.id])):
                temp = self.source[node.iter.id][i]
                if isinstance(node.target, ast.Name):
                    self.source[node.target.id] = temp
                for n in node.body:
                    self.visit(n)
                    self.source[node.iter.id][i] = self.source[node.target.id]
            self.source.pop(node.target.id)


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
    for i in ll:
        i /= i
    for i in range(0, len(ll)):
        ll[i] *= ll[i]
    else:
        b += 1
else:
    c = 2
    while c > 0:
        c -= 1
a = 4
b += a"""
    main(text)
