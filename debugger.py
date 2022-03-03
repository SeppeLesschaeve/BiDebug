import ast
from operations import WhileOperation, FunctionOperation, IfThenElseOperation, ForOperation, CompositeOperation
from forward import ForwardVisitor
from backward import BackwardVisitor
from _ast import withitem, alias, keyword, arg, arguments, ExceptHandler, comprehension, NotIn, NotEq, LtE, Lt, IsNot, \
    Is, In, GtE, Gt, Eq, USub, UAdd, Not, Invert, Sub, RShift, Pow, MatMult, Mult, Mod, LShift, FloorDiv, Div, BitXor, \
    BitOr, BitAnd, Add, Or, And, Store, Load, Del, Tuple, List, Name, Starred, Subscript, Attribute, NamedExpr, \
    Constant, JoinedStr, FormattedValue, Call, Compare, YieldFrom, Yield, Await, GeneratorExp, DictComp, SetComp, \
    ListComp, Set, Dict, IfExp, Lambda, UnaryOp, BinOp, BoolOp, Slice, Continue, Break, Pass, Expr, Nonlocal, Global, \
    ImportFrom, Import, Assert, Try, Raise, AsyncWith, With, If, While, AsyncFor, For, AnnAssign, AugAssign, Assign, \
    Delete, Return, ClassDef, AsyncFunctionDef, FunctionDef, Expression, Interactive, Module, AST
from ast import NameConstant, Bytes, Str, Num, Param, AugStore, AugLoad, Suite, Index, ExtSlice
from collections import deque
from typing import Any


class SourceCreator(ast.NodeVisitor):

    def visit_Module(self, node: Module) -> Any:
        global_part = []
        for program in node.body:
            if not isinstance(program, ast.FunctionDef):
                global_part.append(self.visit(program))
            else:
                self.visit(program)
        global_program = CompositeOperation()
        global_program.operations = global_part
        self.source['globals'] = global_program

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        args = []
        for argument in node.args.args:
            args.append(argument.arg)
        function_def = FunctionOperation(node.name, args)
        self.source[node.name] = function_def
        operations = []
        for statement in node.body:
            operations.append(self.visit(statement))
        for operation in operations:
            operation.parent_operation = function_def
        function_def.operations = operations

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        return node

    def visit_ClassDef(self, node: ClassDef) -> Any:
        return node

    def visit_Return(self, node: Return) -> Any:
        return node

    def visit_Delete(self, node: Delete) -> Any:
        return node

    def visit_Assign(self, node: Assign) -> Any:
        return node

    def visit_AugAssign(self, node: AugAssign) -> Any:
        return node

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        return node

    def visit_For(self, node: For) -> Any:
        for_operation = ForOperation()
        for_operation.target = node.target
        for_operation.iter = node.iter
        operations = []
        for statement in node.body:
            operations.append(self.visit(statement))
        for operation in operations:
            operation.parent_operation = for_operation
        for_operation.operations = operations
        return for_operation

    def visit_AsyncFor(self, node: AsyncFor) -> Any:
        return node

    def visit_While(self, node: While) -> Any:
        while_operation = WhileOperation()
        while_operation.test = node.test
        operations = []
        for statement in node.body:
            operations.append(self.visit(statement))
        for operation in operations:
            operation.parent_operation = while_operation
        while_operation.operations = operations
        return while_operation

    def visit_If(self, node: If) -> Any:
        if_then_else_operation = IfThenElseOperation()
        if_then_else_operation.test = node.test
        operations = []
        then_operations = []
        for statement in node.body:
            then_operations.append(self.visit(statement))
        for operation in then_operations:
            operation.parent_operation = if_then_else_operation
        else_operations = []
        for statement in node.orelse:
            else_operations.append(self.visit(statement))
        for operation in else_operations:
            operation.parent_operation = if_then_else_operation
        for operation in operations:
            operation.parent_operation = if_then_else_operation
        operations.append(then_operations)
        operations.append(else_operations)
        if_then_else_operation.operations = operations
        return if_then_else_operation

    def visit_With(self, node: With) -> Any:
        return node

    def visit_AsyncWith(self, node: AsyncWith) -> Any:
        return node

    def visit_Raise(self, node: Raise) -> Any:
        return node

    def visit_Try(self, node: Try) -> Any:
        return node

    def visit_Assert(self, node: Assert) -> Any:
        return node

    def visit_Import(self, node: Import) -> Any:
        return node

    def visit_ImportFrom(self, node: ImportFrom) -> Any:
        return node

    def visit_Global(self, node: Global) -> Any:
        return node

    def visit_Nonlocal(self, node: Nonlocal) -> Any:
        return node

    def visit_Expr(self, node: Expr) -> Any:
        return node

    def visit_Pass(self, node: Pass) -> Any:
        return node

    def visit_Break(self, node: Break) -> Any:
        return node

    def visit_Continue(self, node: Continue) -> Any:
        return node

    def visit_Slice(self, node: Slice) -> Any:
        return node

    def visit_BoolOp(self, node: BoolOp) -> Any:
        return node

    def visit_BinOp(self, node: BinOp) -> Any:
        return node

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return node

    def visit_Lambda(self, node: Lambda) -> Any:
        return node

    def visit_IfExp(self, node: IfExp) -> Any:
        if_then_else_operation = IfThenElseOperation()
        if_then_else_operation.test = node.test
        operations = [[self.visit(node.body)], [self.visit(node.orelse)]]
        for operation in operations:
            operation.parent_operation = if_then_else_operation
        if_then_else_operation.operations = operations
        return if_then_else_operation

    def visit_Dict(self, node: Dict) -> Any:
        return node

    def visit_Set(self, node: Set) -> Any:
        return node

    def visit_ListComp(self, node: ListComp) -> Any:
        return node

    def visit_SetComp(self, node: SetComp) -> Any:
        return node

    def visit_DictComp(self, node: DictComp) -> Any:
        return node

    def visit_GeneratorExp(self, node: GeneratorExp) -> Any:
        return node

    def visit_Await(self, node: Await) -> Any:
        return node

    def visit_Yield(self, node: Yield) -> Any:
        return node

    def visit_YieldFrom(self, node: YieldFrom) -> Any:
        return node

    def visit_Compare(self, node: Compare) -> Any:
        return node

    def visit_Call(self, node: Call) -> Any:
        return node

    def visit_FormattedValue(self, node: FormattedValue) -> Any:
        return node

    def visit_JoinedStr(self, node: JoinedStr) -> Any:
        return node

    def visit_Constant(self, node: Constant) -> Any:
        return node

    def visit_NamedExpr(self, node: NamedExpr) -> Any:
        return node

    def visit_Attribute(self, node: Attribute) -> Any:
        return node

    def visit_Subscript(self, node: Subscript) -> Any:
        return node

    def visit_Starred(self, node: Starred) -> Any:
        return node

    def visit_Name(self, node: Name) -> Any:
        return node

    def visit_List(self, node: List) -> Any:
        return node

    def visit_Tuple(self, node: Tuple) -> Any:
        return node

    def visit_Del(self, node: Del) -> Any:
        return node

    def visit_Load(self, node: Load) -> Any:
        return node

    def visit_Store(self, node: Store) -> Any:
        return node

    def visit_And(self, node: And) -> Any:
        return node

    def visit_Or(self, node: Or) -> Any:
        return node

    def visit_Add(self, node: Add) -> Any:
        return node

    def visit_BitAnd(self, node: BitAnd) -> Any:
        return node

    def visit_BitOr(self, node: BitOr) -> Any:
        return node

    def visit_BitXor(self, node: BitXor) -> Any:
        return node

    def visit_Div(self, node: Div) -> Any:
        return node

    def visit_FloorDiv(self, node: FloorDiv) -> Any:
        return node

    def visit_LShift(self, node: LShift) -> Any:
        return node

    def visit_Mod(self, node: Mod) -> Any:
        return node

    def visit_Mult(self, node: Mult) -> Any:
        return node

    def visit_MatMult(self, node: MatMult) -> Any:
        return node

    def visit_Pow(self, node: Pow) -> Any:
        return node

    def visit_RShift(self, node: RShift) -> Any:
        return node

    def visit_Sub(self, node: Sub) -> Any:
        return node

    def visit_Invert(self, node: Invert) -> Any:
        return node

    def visit_Not(self, node: Not) -> Any:
        return node

    def visit_UAdd(self, node: UAdd) -> Any:
        return node

    def visit_USub(self, node: USub) -> Any:
        return node

    def visit_Eq(self, node: Eq) -> Any:
        return node

    def visit_Gt(self, node: Gt) -> Any:
        return node

    def visit_GtE(self, node: GtE) -> Any:
        return node

    def visit_In(self, node: In) -> Any:
        return node

    def visit_Is(self, node: Is) -> Any:
        return node

    def visit_IsNot(self, node: IsNot) -> Any:
        return node

    def visit_Lt(self, node: Lt) -> Any:
        return node

    def visit_LtE(self, node: LtE) -> Any:
        return node

    def visit_NotEq(self, node: NotEq) -> Any:
        return node

    def visit_NotIn(self, node: NotIn) -> Any:
        return node

    def visit_comprehension(self, node: comprehension) -> Any:
        return node

    def visit_ExceptHandler(self, node: ExceptHandler) -> Any:
        return node

    def visit_arguments(self, node: arguments) -> Any:
        return node

    def visit_arg(self, node: arg) -> Any:
        return node

    def visit_keyword(self, node: keyword) -> Any:
        return node

    def visit_alias(self, node: alias) -> Any:
        return node

    def visit_withitem(self, node: withitem) -> Any:
        return node

    def visit_ExtSlice(self, node: ExtSlice) -> Any:
        return node

    def visit_Index(self, node: Index) -> Any:
        return node

    def visit_Suite(self, node: Suite) -> Any:
        return node

    def visit_AugLoad(self, node: AugLoad) -> Any:
        return node

    def visit_AugStore(self, node: AugStore) -> Any:
        return node

    def visit_Param(self, node: Param) -> Any:
        return node

    def visit_Num(self, node: Num) -> Any:
        return node

    def visit_Str(self, node: Str) -> Any:
        return node

    def visit_Bytes(self, node: Bytes) -> Any:
        return node

    def visit_NameConstant(self, node: NameConstant) -> Any:
        return node

    def visit_Ellipsis(self, node: Ellipsis) -> Any:
        return node

    def __init__(self, text):
        self.source = {}
        self.tree = None
        self.call_stack = None
        self.build_tree(text)
        self.initialize_stack()

    def build_tree(self, text):
        self.tree = ast.parse(text)
        self.visit(self.tree)
        print(self.source)

    def update(self, source):
        return

    def initialize_stack(self):
        call_stack = deque()
        call_stack.append([self.source['globals'], 0])
        self.call_stack = call_stack


class SourceController:

    def __init__(self, source_creator):
        source = {}
        self.forward_visitor = ForwardVisitor(source, source_creator)
        self.reverse_visitor = BackwardVisitor(source, source_creator)

    def execute(self, number):
        if number == 1:
            self.forward_visitor.execute()
        elif number == 2:
            self.reverse_visitor.execute()


class Debugger:

    def __init__(self, source_controller, source_creator):
        self.source_controller = source_controller
        self.source_creator = source_creator

    def update(self, source):
        self.source_creator.update(source)

    def execute(self, number):
        self.source_controller.execute(number)


def main(source_program):
    source_creator = SourceCreator(source_program)
    source_controller = SourceController(source_creator)
    debugger = Debugger(source_controller, source_creator)
    while True:
        number = int(input())
        if number == 3:
            break
        else:
            debugger.execute(number)


if __name__ == '__main__':
    input_program = """
def test(a, b, l):
    b += 1
    c = 1 + b 
    while b > 1:
        a -= 1
        for x in l:
            if x < 2:
                x = 2
            else:
                x *= 2
        b -= 1        

c = 1
c += 6
def main():
    a = 2
    b = 2
    ll = [1,2,3,4]
    test(a, b, ll)

d = 2    
main()    
"""
    main(input_program)
