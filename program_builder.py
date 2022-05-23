import ast
import copy

import operations
from _ast import withitem, alias, keyword, arg, arguments, ExceptHandler, comprehension, NotIn, NotEq, LtE, Lt, IsNot, \
    Is, In, GtE, Gt, Eq, USub, UAdd, Not, Invert, Sub, RShift, Pow, MatMult, Mult, Mod, LShift, FloorDiv, Div, BitXor, \
    BitOr, BitAnd, Add, Or, And, Store, Load, Del, Tuple, List, Name, Starred, Subscript, Attribute, NamedExpr, \
    Constant, JoinedStr, FormattedValue, Call, Compare, YieldFrom, Yield, Await, GeneratorExp, DictComp, SetComp, \
    ListComp, Set, Dict, IfExp, Lambda, UnaryOp, BinOp, BoolOp, Slice, Continue, Break, Pass, Expr, Nonlocal, Global, \
    ImportFrom, Import, Assert, Try, Raise, AsyncWith, With, If, While, AsyncFor, For, AnnAssign, AugAssign, Assign, \
    Delete, Return, ClassDef, AsyncFunctionDef, FunctionDef, Module
from ast import NameConstant, Bytes, Str, Num, Param, AugStore, AugLoad, Suite, Index, ExtSlice
from typing import Any


class ProgramBuilder(ast.NodeVisitor):

    def visit_Module(self, node: Module) -> Any:
        boot_part = []
        for program in node.body:
            if not isinstance(program, ast.FunctionDef):
                boot_part.append(self.visit(program))
            else:
                self.visit(program)
        boot = [[], boot_part]
        for statement in boot_part:
            statement.parent = boot
        self.functions['boot'] = boot

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        args = []
        for argument in node.args.args:
            args.append(argument.arg)
        ops = []
        for statement in node.body:
            ops.append(self.visit(statement))
        function_def = [args, ops]
        self.functions[node.name] = function_def

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        return node

    def visit_ClassDef(self, node: ClassDef) -> Any:
        return node

    def visit_Return(self, node: Return) -> Any:
        return operations.ReturnOperation([self.visit(node.value)])

    def visit_Delete(self, node: Delete) -> Any:
        return node

    def visit_Assign(self, node: Assign) -> Any:
        targets = []
        for target in node.targets:
            targets.append(target.id)
        ops = [self.visit(node.value)]
        assign_operation = operations.AssignOperation(targets, ops)
        for operation in ops:
            operation.parent = assign_operation
        return assign_operation

    def visit_AugAssign(self, node: AugAssign) -> Any:
        ops = [self.visit(node.value)]
        augassign_operation = operations.AugAssignOperation(node.target.id, ops)
        for operation in ops:
            operation.parent = augassign_operation
        return augassign_operation

    def visit_AnnAssign(self, node: AnnAssign) -> Any:
        return node

    def visit_For(self, node: For) -> Any:
        target = node.target.id
        iter_operation = operations.IterOperation()
        ops = [self.visit(node.iter), iter_operation]
        for statement in node.body:
            ops.append(self.visit(statement))
        for_operation = operations.ForOperation(target, ops)
        for operation in ops:
            operation.parent = for_operation
        return for_operation

    def visit_AsyncFor(self, node: AsyncFor) -> Any:
        return node

    def visit_While(self, node: While) -> Any:
        ops = [self.visit(node.test)]
        for statement in node.body:
            ops.append(self.visit(statement))
        while_operation = operations.WhileOperation(ops)
        for operation in ops:
            operation.parent = while_operation
        return while_operation

    def visit_If(self, node: If) -> Any:
        ops = [self.visit(node.test)]
        then_operations = []
        for statement in node.body:
            then_operations.append(self.visit(statement))
        else_operations = []
        for statement in node.orelse:
            else_operations.append(self.visit(statement))
        for statement in then_operations:
            ops.append(statement)
        for statement in else_operations:
            ops.append(statement)
        if_then_else_operation = operations.IfThenElseOperation(ops, 1 + len(then_operations))
        for operation in then_operations:
            operation.parent = if_then_else_operation
        for operation in else_operations:
            operation.parent = if_then_else_operation
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
        return self.visit(node.value)

    def visit_Pass(self, node: Pass) -> Any:
        return node

    def visit_Break(self, node: Break) -> Any:
        return operations.BreakOperation()

    def visit_Continue(self, node: Continue) -> Any:
        return node

    def visit_Slice(self, node: Slice) -> Any:
        ops = [self.visit(node.lower),self.visit(node.higher),self.viist(node.step)]
        slice_op = operations.SliceOperation(ops)
        for op in ops:
            op.parent = slice_op
        return slice_op

    def visit_BoolOp(self, node: BoolOp) -> Any:
        ops = [self.visit(node.values[0]), self.visit(node.values[1])]
        boolean_operation = operations.BooleanOperation(self.visit(node.op), ops)
        for operation in ops:
            operation.parent = boolean_operation
        return boolean_operation

    def visit_BinOp(self, node: BinOp) -> Any:
        ops = [self.visit(node.left), self.visit(node.right)]
        binary_operation = operations.BinaryOperation(self.visit(node.op), ops)
        for operation in ops:
            operation.parent = binary_operation
        return binary_operation

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return node

    def visit_Lambda(self, node: Lambda) -> Any:
        return node

    def visit_IfExp(self, node: IfExp) -> Any:
        ops = [self.visit(node.test)]
        then_operations = [self.visit(node.body)]
        else_operations = [self.visit(node.orelse)]
        ops.append(then_operations)
        ops.append(else_operations)
        if_then_else_operation = operations.IfThenElseOperation(ops)
        for operation in then_operations:
            operation.parent = if_then_else_operation
        for operation in else_operations:
            operation.parent = if_then_else_operation
        return if_then_else_operation

    def visit_Dict(self, node: Dict) -> Any:
        values = []
        for el in node.values:
            values.append(self.visit(el))
        keys = []
        for key in node.keys:
            keys.append(key.value)
        dict_operation = operations.DictOperation(keys, values)
        for value in values:
            value.parent = dict_operation
        return dict_operation

    def visit_Set(self, node: Set) -> Any:
        elements = []
        for el in node.elts:
            elements.append(self.visit(el))
        set_operation = operations.SetOperation(elements)
        for element in elements:
            element.parent = set_operation
        return set_operation

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
        comparisons = []
        for comparison in node.ops:
            comparisons.append(self.visit(comparison))
        ops = [self.visit(node.left)]
        for operation in node.comparators:
            ops.append(self.visit(operation))
        compare_operation = operations.CompareOperation(comparisons, ops)
        for operation in ops:
            operation.parent = compare_operation
        return compare_operation

    def visit_Call(self, node: Call) -> Any:
        ops = []
        if isinstance(node.func, Attribute):
            target = node.func.value.id
            attr = node.func.attr
            for argument in node.args:
                ops.append(self.visit(argument))
            call_operation = operations.AttributeOperation(target, attr, ops)
        elif isinstance(node.func, Name):
            if node.func.id not in self.functions:
                op = node.func.id
                for argument in node.args:
                    ops.append(self.visit(argument))
                call_operation = operations.BuiltinOperation(op, ops)
            else:
                call_args = []
                for argument in node.args:
                    call_args.append(self.visit(argument))
                copy_of_operations = copy.deepcopy(self.get_function_operations(node.func.id))
                call_operation = operations.CallOperation(node.func.id, call_args, copy_of_operations)
        for operation in ops:
            operation.parent = call_operation
        return call_operation

    def visit_FormattedValue(self, node: FormattedValue) -> Any:
        return node

    def visit_JoinedStr(self, node: JoinedStr) -> Any:
        return node

    def visit_Constant(self, node: Constant) -> Any:
        return operations.ConstantOperation(node.value)

    def visit_NamedExpr(self, node: NamedExpr) -> Any:
        return node

    def visit_Attribute(self, node: Attribute) -> Any:
        return node

    def visit_Subscript(self, node: Subscript) -> Any:
        ops = [self.visit(node.value), self.visit(node.slice)]
        subscript_operation = operations.SubscriptOperation(ops)
        for operation in ops:
            operation.parent = subscript_operation
        return subscript_operation

    def visit_Starred(self, node: Starred) -> Any:
        return node

    def visit_Name(self, node: Name) -> Any:
        return operations.NameOperation(node.id)

    def visit_List(self, node: List) -> Any:
        elements = []
        for el in node.elts:
            elements.append(self.visit(el))
        list_operation = operations.ListOperation(elements)
        for element in elements:
            element.parent = list_operation
        return list_operation

    def visit_Tuple(self, node: Tuple) -> Any:
        return node

    def visit_Del(self, node: Del) -> Any:
        return node

    def visit_Load(self, node: Load) -> Any:
        return node

    def visit_Store(self, node: Store) -> Any:
        return node

    def visit_And(self, node: And) -> Any:
        return operations.enn

    def visit_Or(self, node: Or) -> Any:
        return operations.off

    def visit_Add(self, node: Add) -> Any:
        return operations.add

    def visit_BitAnd(self, node: BitAnd) -> Any:
        return node

    def visit_BitOr(self, node: BitOr) -> Any:
        return node

    def visit_BitXor(self, node: BitXor) -> Any:
        return node

    def visit_Div(self, node: Div) -> Any:
        return operations.div

    def visit_FloorDiv(self, node: FloorDiv) -> Any:
        return node

    def visit_LShift(self, node: LShift) -> Any:
        return node

    def visit_Mod(self, node: Mod) -> Any:
        return node

    def visit_Mult(self, node: Mult) -> Any:
        return operations.mul

    def visit_MatMult(self, node: MatMult) -> Any:
        return node

    def visit_Pow(self, node: Pow) -> Any:
        return node

    def visit_RShift(self, node: RShift) -> Any:
        return node

    def visit_Sub(self, node: Sub) -> Any:
        return operations.sub

    def visit_Invert(self, node: Invert) -> Any:
        return operations.inv

    def visit_Not(self, node: Not) -> Any:
        return operations.nit

    def visit_UAdd(self, node: UAdd) -> Any:
        return operations.adu

    def visit_USub(self, node: USub) -> Any:
        return operations.sbu

    def visit_Eq(self, node: Eq) -> Any:
        return operations.equ

    def visit_Gt(self, node: Gt) -> Any:
        return operations.gth

    def visit_GtE(self, node: GtE) -> Any:
        return operations.gte

    def visit_In(self, node: In) -> Any:
        return operations.inn

    def visit_Is(self, node: Is) -> Any:
        return operations.iss

    def visit_IsNot(self, node: IsNot) -> Any:
        return operations.isn

    def visit_Lt(self, node: Lt) -> Any:
        return operations.lth

    def visit_LtE(self, node: LtE) -> Any:
        return operations.lte

    def visit_NotEq(self, node: NotEq) -> Any:
        return operations.neq

    def visit_NotIn(self, node: NotIn) -> Any:
        return operations.nin

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
        value = self.visit(node.value.op)(node.value.operand.value)
        return operations.ConstantOperation(value)

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
        self.functions = {}
        self.tree = None
        self.build_tree(text)

    def build_tree(self, text):
        self.tree = ast.parse(text)
        self.visit(self.tree)
        print(self.functions)

    def get_function_args(self, name):
        return self.functions[name][0]

    def get_function_operations(self, name):
        return self.functions[name][1]


