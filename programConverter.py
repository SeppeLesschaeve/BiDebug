import ast

assigns = {}

class AssignmentVisitor(ast.NodeVisitor):

    def __init__(self, name):
        self.currentName = name

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id not in assigns:
                    assigns[target.id] = []
                usage_analyzer = AssignmentVisitor(target.id)
                usage_analyzer.visit(node.value)

    def visit_Constant(self, node):
        assigns[self.currentName].append(node.value)


def main(text):
    usage_analyzer = AssignmentVisitor('')
    tree = ast.parse(text)
    print(ast.dump(tree))
    usage_analyzer.visit(tree)
    print(assigns)


if __name__ == '__main__':
    main("""a = 1\nb = 9\nc = 3\na = 3\n""")