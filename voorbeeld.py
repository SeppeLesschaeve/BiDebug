import ast

t = ast.parse("""a.append(1)""")
print(t)