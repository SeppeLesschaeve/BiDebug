import ast

assignments = {}

class AssignmentVisitor(ast.NodeVisitor):

    def __init__(self):
        self.leftOperand = ''
        self.rightOperand = ''
    def translateToOp(self,op):
        if isinstance(op,ast.Eq):
            def eq(x,y):
                return x == y
            return eq
        if isinstance(op,ast.NotEq):
            def neq(x,y):
                return x != y
            return neq
        if isinstance(op,ast.In):
            def inf(x,y):
                return x in y
            return inf
        if isinstance(op,ast.NotIn):
            def nin(x,y):
                return x not in y
            return nin
    def visit_Add(self, node):
        assignments.get(self.leftOperand) + assignments.get(self.rightOperand)
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) & isinstance(node.value, ast.Constant):
                assignments[target.id] = node.value.value
    def visit_AugAssign(self, node):
        if isinstance(node.value, ast.Name) & isinstance(node.target, ast.Name):
            assignments[node.target.id] = assignments.get(node.target.id) + assignments.get(node.value.id)
    def visit_BinOp(self, node):
        if isinstance(node.left, ast.Name) & isinstance(node.right, ast.Name):
            self.leftOperand = node.left.id
            self.rightOperand = node.right.id
        if isinstance(node.op, ast.Add):
            self.visit_Add(node.op)
    def visit_Compare(self, node):
        ops = node.ops
        comps = node.comparators
        if len(comps) == 1:
            op = self.translateToOp(ops[0])
            binop = ast.BinOp(op=op,left=node.left,right=comps[0])
            return self.visit(binop)
        left = node.left
        values = []
        for op,comp in zip(ops,comps):
            new_node = self.visit(ast.Compare(comparators=[comp],left=left,ops=[self.translateToOp(op)]))
            left = comp
            values.append(new_node)
        return self.visit(ast.BoolOp(op=ast.And(),values=values))

        
        print(node.left)
    def visit_Constant(self, node):
        return node.value
    def visit_Expr(self, node):
        if isinstance(node.value, ast.BinOp):
            self.visit_BinOp(node.value)
    def visit_If(self, node):
        if self.visit(node.test):
            for n in node.body:
                self.visit(n)
        elif node.orelse:
            for n in node.orelse:
                self.visit(n)
    def visit_While(self, node):
        while self.visit(node.test):
            for n in node.body:
                self.visit(n)
        if node.orelse:
            for n in node.orelse:
                self.visit(n)
def main(text):
    usage_analyzer = AssignmentVisitor()
    tree = ast.parse(text)
    #print(ast.dump(tree))
    usage_analyzer.visit(tree)
    print(assignments)


if __name__ == '__main__':
    main("""a = 1\nb = 9\nwhile b + 1 == 9 + 1 and a == 1:\n\tb = 1\nc = 4\na = 3\na + c\na += c\nb = a + c\nif False:\n\ta = False\nelse:\n\ta = True""")