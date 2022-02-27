import ast
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


class Operation:

    def __init__(self):
        self.parent_operation = None

    def update_next(self):
        return

    def update_previous(self):
        return


class CompositeOperation(Operation):

    def __init__(self):
        Operation.__init__(self)
        self.operations = []
        self.current = 0

    def current_operation(self):
        return self.operations[self.current]


class IfThenElseOperation(CompositeOperation):

    def __init__(self):
        self.choices_stack = []
        CompositeOperation.__init__(self)
        self.current = -1

    def update_previous(self):
        self.choices_stack.pop()

    def current_operation(self):
        if self.current == -1:
            return self.operations[0]
        else:
            if self.choices_stack[-1] == 1:
                return self.operations[1][self.current]
            else:
                return self.operations[2][self.current]


class WhileOperation(CompositeOperation):

    def __init__(self):
        self.number = 0
        CompositeOperation.__init__(self)

    def update_next(self):
        self.number += 1

    def update_previous(self):
        self.number -= 1

    def current_operation(self):
        if self.current == -1:
            return self.operations[0]
        else:
            return self.operations[1][self.current]


class ForOperation(CompositeOperation):

    def __init__(self):
        self.index = 0
        self.collection = []
        CompositeOperation.__init__(self)

    def update_next(self):
        self.index += 1

    def update_previous(self):
        self.index -= 1

    def current_operation(self):
        if self.current == -1:
            return self.operations[0]
        else:
            return self.operations[1][self.current]


class FunctionOperation(CompositeOperation):

    def __init__(self):
        self.arguments = None
        CompositeOperation.__init__(self)


class ReverseVisitor(ast.NodeVisitor):

    def visit(self, node: AST) -> Any:
        return super().visit(node)

    def generic_visit(self, node: AST) -> Any:
        return super().generic_visit(node)

    def visit_Module(self, node: Module) -> Any:
        return super().visit_Module(node)

    def visit_Interactive(self, node: Interactive) -> Any:
        return super().visit_Interactive(node)

    def visit_Expression(self, node: Expression) -> Any:
        return super().visit_Expression(node)

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        return super().visit_FunctionDef(node)

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        return super().visit_AsyncFunctionDef(node)

    def visit_ClassDef(self, node: ClassDef) -> Any:
        return super().visit_ClassDef(node)

    def visit_Return(self, node: Return) -> Any:
        return super().visit_Return(node)

    def visit_Delete(self, node: Delete) -> Any:
        return super().visit_Delete(node)

    def visit_Assign(self, node: Assign) -> Any:
        return super().visit_Assign(node)

    def visit_AugAssign(self, node: AugAssign) -> Any:
        return super().visit_AugAssign(node)

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        return super().visit_AnnAssign(node)

    def visit_For(self, node: For) -> Any:
        return super().visit_For(node)

    def visit_AsyncFor(self, node: AsyncFor) -> Any:
        return super().visit_AsyncFor(node)

    def visit_While(self, node: While) -> Any:
        return super().visit_While(node)

    def visit_If(self, node: If) -> Any:
        return super().visit_If(node)

    def visit_With(self, node: With) -> Any:
        return super().visit_With(node)

    def visit_AsyncWith(self, node: AsyncWith) -> Any:
        return super().visit_AsyncWith(node)

    def visit_Raise(self, node: Raise) -> Any:
        return super().visit_Raise(node)

    def visit_Try(self, node: Try) -> Any:
        return super().visit_Try(node)

    def visit_Assert(self, node: Assert) -> Any:
        return super().visit_Assert(node)

    def visit_Import(self, node: Import) -> Any:
        return super().visit_Import(node)

    def visit_ImportFrom(self, node: ImportFrom) -> Any:
        return super().visit_ImportFrom(node)

    def visit_Global(self, node: Global) -> Any:
        return super().visit_Global(node)

    def visit_Nonlocal(self, node: Nonlocal) -> Any:
        return super().visit_Nonlocal(node)

    def visit_Expr(self, node: Expr) -> Any:
        return super().visit_Expr(node)

    def visit_Pass(self, node: Pass) -> Any:
        return super().visit_Pass(node)

    def visit_Break(self, node: Break) -> Any:
        return super().visit_Break(node)

    def visit_Continue(self, node: Continue) -> Any:
        return super().visit_Continue(node)

    def visit_Slice(self, node: Slice) -> Any:
        return super().visit_Slice(node)

    def visit_BoolOp(self, node: BoolOp) -> Any:
        return super().visit_BoolOp(node)

    def visit_BinOp(self, node: BinOp) -> Any:
        return super().visit_BinOp(node)

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return super().visit_UnaryOp(node)

    def visit_Lambda(self, node: Lambda) -> Any:
        return super().visit_Lambda(node)

    def visit_IfExp(self, node: IfExp) -> Any:
        return super().visit_IfExp(node)

    def visit_Dict(self, node: Dict) -> Any:
        return super().visit_Dict(node)

    def visit_Set(self, node: Set) -> Any:
        return super().visit_Set(node)

    def visit_ListComp(self, node: ListComp) -> Any:
        return super().visit_ListComp(node)

    def visit_SetComp(self, node: SetComp) -> Any:
        return super().visit_SetComp(node)

    def visit_DictComp(self, node: DictComp) -> Any:
        return super().visit_DictComp(node)

    def visit_GeneratorExp(self, node: GeneratorExp) -> Any:
        return super().visit_GeneratorExp(node)

    def visit_Await(self, node: Await) -> Any:
        return super().visit_Await(node)

    def visit_Yield(self, node: Yield) -> Any:
        return super().visit_Yield(node)

    def visit_YieldFrom(self, node: YieldFrom) -> Any:
        return super().visit_YieldFrom(node)

    def visit_Compare(self, node: Compare) -> Any:
        return super().visit_Compare(node)

    def visit_Call(self, node: Call) -> Any:
        return super().visit_Call(node)

    def visit_FormattedValue(self, node: FormattedValue) -> Any:
        return super().visit_FormattedValue(node)

    def visit_JoinedStr(self, node: JoinedStr) -> Any:
        return super().visit_JoinedStr(node)

    def visit_Constant(self, node: Constant) -> Any:
        return super().visit_Constant(node)

    def visit_NamedExpr(self, node: NamedExpr) -> Any:
        return super().visit_NamedExpr(node)

    def visit_Attribute(self, node: Attribute) -> Any:
        return super().visit_Attribute(node)

    def visit_Subscript(self, node: Subscript) -> Any:
        return super().visit_Subscript(node)

    def visit_Starred(self, node: Starred) -> Any:
        return super().visit_Starred(node)

    def visit_Name(self, node: Name) -> Any:
        return super().visit_Name(node)

    def visit_List(self, node: List) -> Any:
        return super().visit_List(node)

    def visit_Tuple(self, node: Tuple) -> Any:
        return super().visit_Tuple(node)

    def visit_Del(self, node: Del) -> Any:
        return super().visit_Del(node)

    def visit_Load(self, node: Load) -> Any:
        return super().visit_Load(node)

    def visit_Store(self, node: Store) -> Any:
        return super().visit_Store(node)

    def visit_And(self, node: And) -> Any:
        return super().visit_And(node)

    def visit_Or(self, node: Or) -> Any:
        return super().visit_Or(node)

    def visit_Add(self, node: Add) -> Any:
        return super().visit_Add(node)

    def visit_BitAnd(self, node: BitAnd) -> Any:
        return super().visit_BitAnd(node)

    def visit_BitOr(self, node: BitOr) -> Any:
        return super().visit_BitOr(node)

    def visit_BitXor(self, node: BitXor) -> Any:
        return super().visit_BitXor(node)

    def visit_Div(self, node: Div) -> Any:
        return super().visit_Div(node)

    def visit_FloorDiv(self, node: FloorDiv) -> Any:
        return super().visit_FloorDiv(node)

    def visit_LShift(self, node: LShift) -> Any:
        return super().visit_LShift(node)

    def visit_Mod(self, node: Mod) -> Any:
        return super().visit_Mod(node)

    def visit_Mult(self, node: Mult) -> Any:
        return super().visit_Mult(node)

    def visit_MatMult(self, node: MatMult) -> Any:
        return super().visit_MatMult(node)

    def visit_Pow(self, node: Pow) -> Any:
        return super().visit_Pow(node)

    def visit_RShift(self, node: RShift) -> Any:
        return super().visit_RShift(node)

    def visit_Sub(self, node: Sub) -> Any:
        return super().visit_Sub(node)

    def visit_Invert(self, node: Invert) -> Any:
        return super().visit_Invert(node)

    def visit_Not(self, node: Not) -> Any:
        return super().visit_Not(node)

    def visit_UAdd(self, node: UAdd) -> Any:
        return super().visit_UAdd(node)

    def visit_USub(self, node: USub) -> Any:
        return super().visit_USub(node)

    def visit_Eq(self, node: Eq) -> Any:
        return super().visit_Eq(node)

    def visit_Gt(self, node: Gt) -> Any:
        return super().visit_Gt(node)

    def visit_GtE(self, node: GtE) -> Any:
        return super().visit_GtE(node)

    def visit_In(self, node: In) -> Any:
        return super().visit_In(node)

    def visit_Is(self, node: Is) -> Any:
        return super().visit_Is(node)

    def visit_IsNot(self, node: IsNot) -> Any:
        return super().visit_IsNot(node)

    def visit_Lt(self, node: Lt) -> Any:
        return super().visit_Lt(node)

    def visit_LtE(self, node: LtE) -> Any:
        return super().visit_LtE(node)

    def visit_NotEq(self, node: NotEq) -> Any:
        return super().visit_NotEq(node)

    def visit_NotIn(self, node: NotIn) -> Any:
        return super().visit_NotIn(node)

    def visit_comprehension(self, node: comprehension) -> Any:
        return super().visit_comprehension(node)

    def visit_ExceptHandler(self, node: ExceptHandler) -> Any:
        return super().visit_ExceptHandler(node)

    def visit_arguments(self, node: arguments) -> Any:
        return super().visit_arguments(node)

    def visit_arg(self, node: arg) -> Any:
        return super().visit_arg(node)

    def visit_keyword(self, node: keyword) -> Any:
        return super().visit_keyword(node)

    def visit_alias(self, node: alias) -> Any:
        return super().visit_alias(node)

    def visit_withitem(self, node: withitem) -> Any:
        return super().visit_withitem(node)

    def visit_ExtSlice(self, node: ExtSlice) -> Any:
        return super().visit_ExtSlice(node)

    def visit_Index(self, node: Index) -> Any:
        return super().visit_Index(node)

    def visit_Suite(self, node: Suite) -> Any:
        return super().visit_Suite(node)

    def visit_AugLoad(self, node: AugLoad) -> Any:
        return super().visit_AugLoad(node)

    def visit_AugStore(self, node: AugStore) -> Any:
        return super().visit_AugStore(node)

    def visit_Param(self, node: Param) -> Any:
        return super().visit_Param(node)

    def visit_Num(self, node: Num) -> Any:
        return super().visit_Num(node)

    def visit_Str(self, node: Str) -> Any:
        return super().visit_Str(node)

    def visit_Bytes(self, node: Bytes) -> Any:
        return super().visit_Bytes(node)

    def visit_NameConstant(self, node: NameConstant) -> Any:
        return super().visit_NameConstant(node)

    def visit_Ellipsis(self, node: Ellipsis) -> Any:
        return super().visit_Ellipsis(node)

    def __init__(self):
        self.source = None

    def execute(self, operation):
        self.visit(operation)


class ForwardVisitor(ast.NodeVisitor):

    def visit(self, node: AST) -> Any:
        return super().visit(node)

    def generic_visit(self, node: AST) -> Any:
        return super().generic_visit(node)

    def visit_Module(self, node: Module) -> Any:
        return super().visit_Module(node)

    def visit_Interactive(self, node: Interactive) -> Any:
        return super().visit_Interactive(node)

    def visit_Expression(self, node: Expression) -> Any:
        return super().visit_Expression(node)

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        return super().visit_FunctionDef(node)

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        return super().visit_AsyncFunctionDef(node)

    def visit_ClassDef(self, node: ClassDef) -> Any:
        return super().visit_ClassDef(node)

    def visit_Return(self, node: Return) -> Any:
        return super().visit_Return(node)

    def visit_Delete(self, node: Delete) -> Any:
        return super().visit_Delete(node)

    def visit_Assign(self, node: Assign) -> Any:
        return super().visit_Assign(node)

    def visit_AugAssign(self, node: AugAssign) -> Any:
        return super().visit_AugAssign(node)

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        return super().visit_AnnAssign(node)

    def visit_For(self, node: For) -> Any:
        return super().visit_For(node)

    def visit_AsyncFor(self, node: AsyncFor) -> Any:
        return super().visit_AsyncFor(node)

    def visit_While(self, node: While) -> Any:
        return super().visit_While(node)

    def visit_If(self, node: If) -> Any:
        return super().visit_If(node)

    def visit_With(self, node: With) -> Any:
        return super().visit_With(node)

    def visit_AsyncWith(self, node: AsyncWith) -> Any:
        return super().visit_AsyncWith(node)

    def visit_Raise(self, node: Raise) -> Any:
        return super().visit_Raise(node)

    def visit_Try(self, node: Try) -> Any:
        return super().visit_Try(node)

    def visit_Assert(self, node: Assert) -> Any:
        return super().visit_Assert(node)

    def visit_Import(self, node: Import) -> Any:
        return super().visit_Import(node)

    def visit_ImportFrom(self, node: ImportFrom) -> Any:
        return super().visit_ImportFrom(node)

    def visit_Global(self, node: Global) -> Any:
        return super().visit_Global(node)

    def visit_Nonlocal(self, node: Nonlocal) -> Any:
        return super().visit_Nonlocal(node)

    def visit_Expr(self, node: Expr) -> Any:
        return super().visit_Expr(node)

    def visit_Pass(self, node: Pass) -> Any:
        return super().visit_Pass(node)

    def visit_Break(self, node: Break) -> Any:
        return super().visit_Break(node)

    def visit_Continue(self, node: Continue) -> Any:
        return super().visit_Continue(node)

    def visit_Slice(self, node: Slice) -> Any:
        return super().visit_Slice(node)

    def visit_BoolOp(self, node: BoolOp) -> Any:
        return super().visit_BoolOp(node)

    def visit_BinOp(self, node: BinOp) -> Any:
        return super().visit_BinOp(node)

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return super().visit_UnaryOp(node)

    def visit_Lambda(self, node: Lambda) -> Any:
        return super().visit_Lambda(node)

    def visit_IfExp(self, node: IfExp) -> Any:
        return super().visit_IfExp(node)

    def visit_Dict(self, node: Dict) -> Any:
        return super().visit_Dict(node)

    def visit_Set(self, node: Set) -> Any:
        return super().visit_Set(node)

    def visit_ListComp(self, node: ListComp) -> Any:
        return super().visit_ListComp(node)

    def visit_SetComp(self, node: SetComp) -> Any:
        return super().visit_SetComp(node)

    def visit_DictComp(self, node: DictComp) -> Any:
        return super().visit_DictComp(node)

    def visit_GeneratorExp(self, node: GeneratorExp) -> Any:
        return super().visit_GeneratorExp(node)

    def visit_Await(self, node: Await) -> Any:
        return super().visit_Await(node)

    def visit_Yield(self, node: Yield) -> Any:
        return super().visit_Yield(node)

    def visit_YieldFrom(self, node: YieldFrom) -> Any:
        return super().visit_YieldFrom(node)

    def visit_Compare(self, node: Compare) -> Any:
        return super().visit_Compare(node)

    def visit_Call(self, node: Call) -> Any:
        return super().visit_Call(node)

    def visit_FormattedValue(self, node: FormattedValue) -> Any:
        return super().visit_FormattedValue(node)

    def visit_JoinedStr(self, node: JoinedStr) -> Any:
        return super().visit_JoinedStr(node)

    def visit_Constant(self, node: Constant) -> Any:
        return super().visit_Constant(node)

    def visit_NamedExpr(self, node: NamedExpr) -> Any:
        return super().visit_NamedExpr(node)

    def visit_Attribute(self, node: Attribute) -> Any:
        return super().visit_Attribute(node)

    def visit_Subscript(self, node: Subscript) -> Any:
        return super().visit_Subscript(node)

    def visit_Starred(self, node: Starred) -> Any:
        return super().visit_Starred(node)

    def visit_Name(self, node: Name) -> Any:
        return super().visit_Name(node)

    def visit_List(self, node: List) -> Any:
        return super().visit_List(node)

    def visit_Tuple(self, node: Tuple) -> Any:
        return super().visit_Tuple(node)

    def visit_Del(self, node: Del) -> Any:
        return super().visit_Del(node)

    def visit_Load(self, node: Load) -> Any:
        return super().visit_Load(node)

    def visit_Store(self, node: Store) -> Any:
        return super().visit_Store(node)

    def visit_And(self, node: And) -> Any:
        return super().visit_And(node)

    def visit_Or(self, node: Or) -> Any:
        return super().visit_Or(node)

    def visit_Add(self, node: Add) -> Any:
        return super().visit_Add(node)

    def visit_BitAnd(self, node: BitAnd) -> Any:
        return super().visit_BitAnd(node)

    def visit_BitOr(self, node: BitOr) -> Any:
        return super().visit_BitOr(node)

    def visit_BitXor(self, node: BitXor) -> Any:
        return super().visit_BitXor(node)

    def visit_Div(self, node: Div) -> Any:
        return super().visit_Div(node)

    def visit_FloorDiv(self, node: FloorDiv) -> Any:
        return super().visit_FloorDiv(node)

    def visit_LShift(self, node: LShift) -> Any:
        return super().visit_LShift(node)

    def visit_Mod(self, node: Mod) -> Any:
        return super().visit_Mod(node)

    def visit_Mult(self, node: Mult) -> Any:
        return super().visit_Mult(node)

    def visit_MatMult(self, node: MatMult) -> Any:
        return super().visit_MatMult(node)

    def visit_Pow(self, node: Pow) -> Any:
        return super().visit_Pow(node)

    def visit_RShift(self, node: RShift) -> Any:
        return super().visit_RShift(node)

    def visit_Sub(self, node: Sub) -> Any:
        return super().visit_Sub(node)

    def visit_Invert(self, node: Invert) -> Any:
        return super().visit_Invert(node)

    def visit_Not(self, node: Not) -> Any:
        return super().visit_Not(node)

    def visit_UAdd(self, node: UAdd) -> Any:
        return super().visit_UAdd(node)

    def visit_USub(self, node: USub) -> Any:
        return super().visit_USub(node)

    def visit_Eq(self, node: Eq) -> Any:
        return super().visit_Eq(node)

    def visit_Gt(self, node: Gt) -> Any:
        return super().visit_Gt(node)

    def visit_GtE(self, node: GtE) -> Any:
        return super().visit_GtE(node)

    def visit_In(self, node: In) -> Any:
        return super().visit_In(node)

    def visit_Is(self, node: Is) -> Any:
        return super().visit_Is(node)

    def visit_IsNot(self, node: IsNot) -> Any:
        return super().visit_IsNot(node)

    def visit_Lt(self, node: Lt) -> Any:
        return super().visit_Lt(node)

    def visit_LtE(self, node: LtE) -> Any:
        return super().visit_LtE(node)

    def visit_NotEq(self, node: NotEq) -> Any:
        return super().visit_NotEq(node)

    def visit_NotIn(self, node: NotIn) -> Any:
        return super().visit_NotIn(node)

    def visit_comprehension(self, node: comprehension) -> Any:
        return super().visit_comprehension(node)

    def visit_ExceptHandler(self, node: ExceptHandler) -> Any:
        return super().visit_ExceptHandler(node)

    def visit_arguments(self, node: arguments) -> Any:
        return super().visit_arguments(node)

    def visit_arg(self, node: arg) -> Any:
        return super().visit_arg(node)

    def visit_keyword(self, node: keyword) -> Any:
        return super().visit_keyword(node)

    def visit_alias(self, node: alias) -> Any:
        return super().visit_alias(node)

    def visit_withitem(self, node: withitem) -> Any:
        return super().visit_withitem(node)

    def visit_ExtSlice(self, node: ExtSlice) -> Any:
        return super().visit_ExtSlice(node)

    def visit_Index(self, node: Index) -> Any:
        return super().visit_Index(node)

    def visit_Suite(self, node: Suite) -> Any:
        return super().visit_Suite(node)

    def visit_AugLoad(self, node: AugLoad) -> Any:
        return super().visit_AugLoad(node)

    def visit_AugStore(self, node: AugStore) -> Any:
        return super().visit_AugStore(node)

    def visit_Param(self, node: Param) -> Any:
        return super().visit_Param(node)

    def visit_Num(self, node: Num) -> Any:
        return super().visit_Num(node)

    def visit_Str(self, node: Str) -> Any:
        return super().visit_Str(node)

    def visit_Bytes(self, node: Bytes) -> Any:
        return super().visit_Bytes(node)

    def visit_NameConstant(self, node: NameConstant) -> Any:
        return super().visit_NameConstant(node)

    def visit_Ellipsis(self, node: Ellipsis) -> Any:
        return super().visit_Ellipsis(node)

    def __init__(self):
        self.source = None

    def execute(self, operation):
        self.visit(operation)


class SourceCreator(ast.NodeVisitor):

    def visit_Module(self, node: Module) -> Any:
        for program in node.body:
            self.visit(program)

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        function_def = FunctionOperation()
        function_def.name = node.name
        args = {}
        for argument in node.args.args:
            args[argument.arg] = []
        function_def.arguments = args
        operations = []
        for statement in node.body:
            operations.append(self.visit(statement))
        for operation in operations:
            operation.parent_operation = function_def
        function_def.operations = operations
        self.source[node.name] = function_def

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
        operations = [node.test]
        while_operations = []
        for statement in node.body:
            while_operations.append(self.visit(statement))
        for operation in while_operations:
            operation.parent_operation = while_operation
        for operation in operations:
            operation.parent_operation = while_operation
        operations.append(while_operations)
        while_operation.operations = operations
        return while_operation

    def visit_If(self, node: If) -> Any:
        if_then_else_operation = IfThenElseOperation()
        operations = [node.test]
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
        operations = [node.test, [self.visit(node.body)], [self.visit(node.orelse)]]
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

    def __init__(self):
        self.tree = None
        self.source = {}

    def build_tree(self, text):
        self.tree = ast.parse(text)
        self.visit(self.tree)
        print(self.source)

    def update(self, source):
        return


class SourceController:

    def __init__(self):
        self.forward_visitor = ForwardVisitor()
        self.reverse_visitor = ReverseVisitor()

    def execute(self, number, operation):
        if number == 1:
            self.forward_visitor.execute(operation)
        elif number == 2:
            self.reverse_visitor.execute(operation)


class Debugger:

    def __init__(self, source_controller, source_creator):
        self.source_controller = source_controller
        self.source_creator = source_creator
        self.call_stack = deque()
        self.call_stack.append('main')

    def current_operation(self):
        if self.call_stack:
            return self.source_creator.source[self.call_stack[-1]].current_operation()
        else:
            return None

    def update(self, source):
        self.source_creator.update(source)

    def execute(self, number):
        self.source_controller.execute(number, self.current_operation())


def main(source):
    source_creator = SourceCreator()
    source_creator.build_tree(source)
    source_controller = SourceController()
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

def main():
    a = 2
    b = 2
    ll = [1,2,3,4]
    test(a, b, ll)
    
main()    
"""
    main(input_program)
