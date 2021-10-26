import ast

assigns = {}

class AssignmentVisitor(ast.NodeVisitor):

    def __init__(self):
        self.leftOperand = ''
        self.rightOperand = ''

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) & isinstance(node.value, ast.Constant):
                if target.id not in assigns:
                    assigns[target.id] = [node.value.value]
                else:
                    assigns.get(target.id).insert(0, node.value.value)

    def visit_Add(self, node):
        print(assigns.get(self.leftOperand)[0] + assigns.get(self.rightOperand)[0])

    def visit_AugAssign(self, node):
        if isinstance(node.value, ast.Name) & isinstance(node.target, ast.Name):
            assigns.get(node.target.id).insert(0, assigns.get(node.target.id)[0] + assigns.get(node.value.id)[0])

    def visit_BinOp(self, node):
        if isinstance(node.left, ast.Name) & isinstance(node.right, ast.Name):
            self.leftOperand = node.left.id
            self.rightOperand = node.right.id
        if isinstance(node.op, ast.Add):
            self.visit_Add(node.op)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.BinOp):
            self.visit_BinOp(node.value)


def main(text):
    usage_analyzer = AssignmentVisitor()
    tree = ast.parse(text)
    print(ast.dump(tree))
    usage_analyzer.visit(tree)
    print(assigns)


if __name__ == '__main__':
    main("""a = 1\nb = 9\nc = 4\na = 3\na + c\na += c\n""")