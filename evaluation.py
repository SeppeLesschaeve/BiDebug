from operations import ConstantOperation, NameOperation, BinaryOperation, CallOperation, \
    SubscriptOperation, CompareOperation, ListOperation, ReturnOperation, BreakOperation, IfThenElseOperation, \
    AssignOperation

class Evaluator:

    def __init__(self, source_creator):
        self.source_creator = source_creator

    def evaluate_constant(self, el: ConstantOperation):
        el.eval = el.value

    def evaluate_name(self, el: NameOperation):
        el.eval = self.source_creator.get_active_source(el.ref)[-1]

    def evaluate_binop(self, el: BinaryOperation):
        el.state.evaluate()

    def evaluate_call(self, el: CallOperation):
        el.state.evaluate()

    def evaluate_subscript(self, el: SubscriptOperation):
        el.slice.evaluate()
        el.value.evaluate()
        el.eval = el.set_elements()

    def evaluate_compare(self, el: CompareOperation):
        el.left.evaluate()
        for comparator in el.comparators:
            comparator.evaluate()
        el.eval = True
        for i in range(len(el.comparisons)):
            el.eval = el.eval and el.comparisons[i](el.comparators[i].eval, el.comparators[i + 1].eval)

    def evaluate_list(self, el: ListOperation):
        el.eval = []
        for elem in el.elts:
            elem.evaluate()
            el.eval.append(elem.eval)

    def evaluate_return(self, el: ReturnOperation):
        try:
            el.value.evaluate()
            el.eval = el.value.eval
            self.source_creator.get_control_function().get_source()['return'] = el.eval
        except AttributeError:
            self.source_creator.get_control_function().get_source()['return'] = None

    def evaluate_break(self, el: BreakOperation):
        operation = self.source_creator.get_control_function().operation
        control_operation = operation.parent_operation
        while isinstance(control_operation, IfThenElseOperation):
            control_operation = control_operation.parent_operation
        control_operation.parent_operation.increment_current()
        self.source_creator.get_control_function().update_operation(control_operation.parent_operation)
        raise Exception

    def evaluate_assign(self, el: AssignOperation):
        for target in el.targets:
            try:
                target.evaluate(self)
                target.eval.append(el.eval)
            except :
                key = self.source_creator.add_value(el.eval)
                func = self.source_creator.get_control_function()
                func.add(target.ref, key)
