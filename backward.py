import ast

import operations
from operations import WhileOperation, FunctionOperation, IfThenElseOperation, ForOperation
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

class BackwardVisitor(ast.NodeVisitor):

    def evaluate(self, operand):
        if isinstance(operand, str):
            return self.source_creator.get_active_source(operand)[-1]
        elif isinstance(operand, Call):
            result = self.source_creator.functions[self.visit(operand.func)].source[-1]['return']
            self.source_creator.functions[self.visit(operand.func)].source.pop()
            return result
        else:
            return operand

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
        targets = []
        for target in node.targets:
            targets.append(self.visit(target))
        for target in targets:
            self.source_creator.get_active_source(target).pop()

    def visit_AugAssign(self, node: AugAssign) -> Any:
        target = self.visit(node.target)
        source = self.source_creator.get_active_source(target)
        value = self.visit(node.op)(source[-1], self.evaluate(node.value))
        source[-1] = value

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
        self.visit(node.value)

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
        return self.visit(node.op)(self.evaluate(self.visit(node.left)), self.evaluate(self.visit(node.right)))

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
        comparators = [self.evaluate(self.visit(node.left))]
        for comparator in node.comparators:
            comparators.append(self.evaluate(self.visit(comparator)))
        comparisons = []
        for comparison in node.ops:
            comparisons.append(comparison)
        value = True
        for i in range(len(comparisons)):
            value = value and self.visit(comparisons[i])(self.evaluate(comparators[i]), self.evaluate(comparators[i+1]))
        return value

    def visit_Call(self, node: Call) -> Any:
        return super().visit_Call(node)

    def visit_FormattedValue(self, node: FormattedValue) -> Any:
        return super().visit_FormattedValue(node)

    def visit_JoinedStr(self, node: JoinedStr) -> Any:
        return super().visit_JoinedStr(node)

    def visit_Constant(self, node: Constant) -> Any:
        return node.value

    def visit_NamedExpr(self, node: NamedExpr) -> Any:
        return super().visit_NamedExpr(node)

    def visit_Attribute(self, node: Attribute) -> Any:
        return super().visit_Attribute(node)

    def visit_Subscript(self, node: Subscript) -> Any:
        return super().visit_Subscript(node)

    def visit_Starred(self, node: Starred) -> Any:
        return super().visit_Starred(node)

    def visit_Name(self, node: Name) -> Any:
        return node.id

    def visit_List(self, node: List) -> Any:
        elements = []
        for el in node.elts:
            elements.append(self.visit(el))
        return elements

    def visit_Tuple(self, node: Tuple) -> Any:
        elements = []
        for el in node.elts:
            elements.append(self.visit(el))
        return elements

    def visit_Del(self, node: Del) -> Any:
        return super().visit_Del(node)

    def visit_Load(self, node: Load) -> Any:
        return super().visit_Load(node)

    def visit_Store(self, node: Store) -> Any:
        return super().visit_Store(node)

    def visit_And(self, node: And) -> Any:
        return operations.en

    def visit_Or(self, node: Or) -> Any:
        return operations.of

    def visit_Add(self, node: Add) -> Any:
        return operations.sub

    def visit_BitAnd(self, node: BitAnd) -> Any:
        return super().visit_BitAnd(node)

    def visit_BitOr(self, node: BitOr) -> Any:
        return super().visit_BitOr(node)

    def visit_BitXor(self, node: BitXor) -> Any:
        return super().visit_BitXor(node)

    def visit_Div(self, node: Div) -> Any:
        return operations.mul

    def visit_FloorDiv(self, node: FloorDiv) -> Any:
        return super().visit_FloorDiv(node)

    def visit_LShift(self, node: LShift) -> Any:
        return super().visit_LShift(node)

    def visit_Mod(self, node: Mod) -> Any:
        return super().visit_Mod(node)

    def visit_Mult(self, node: Mult) -> Any:
        return operations.div

    def visit_MatMult(self, node: MatMult) -> Any:
        return super().visit_MatMult(node)

    def visit_Pow(self, node: Pow) -> Any:
        return super().visit_Pow(node)

    def visit_RShift(self, node: RShift) -> Any:
        return super().visit_RShift(node)

    def visit_Sub(self, node: Sub) -> Any:
        return operations.add

    def visit_Invert(self, node: Invert) -> Any:
        return super().visit_Invert(node)

    def visit_Not(self, node: Not) -> Any:
        return operations.niet

    def visit_UAdd(self, node: UAdd) -> Any:
        return super().visit_UAdd(node)

    def visit_USub(self, node: USub) -> Any:
        return super().visit_USub(node)

    def visit_Eq(self, node: Eq) -> Any:
        return operations.eq

    def visit_Gt(self, node: Gt) -> Any:
        return operations.gt

    def visit_GtE(self, node: GtE) -> Any:
        return operations.gte

    def visit_In(self, node: In) -> Any:
        return operations.inn

    def visit_Is(self, node: Is) -> Any:
        return operations.iss

    def visit_IsNot(self, node: IsNot) -> Any:
        return operations.nis

    def visit_Lt(self, node: Lt) -> Any:
        return operations.lt

    def visit_LtE(self, node: LtE) -> Any:
        return operations.lte

    def visit_NotEq(self, node: NotEq) -> Any:
        return operations.neq

    def visit_NotIn(self, node: NotIn) -> Any:
        return operations.nin

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

    def __init__(self, source_creator):
        self.source_creator = source_creator
        self.debugger = None

    def execute(self):
        control_operation = self.source_creator.call_stack[-1][0]
        operation = control_operation.operations[self.source_creator.call_stack[-1][1]]
        self.visit(operation)
        if control_operation == self.source_creator.call_stack[-1][0]:
            control_operation.update_backward(self.source_creator.call_stack, self)
        print(operation)
