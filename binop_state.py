class LeftState:

    def __init__(self, binop):
        self.binop = binop

    def evaluate(self):
        self.binop.left.evaluate()
        if self.binop.left.is_forward_completed():
            self.binop.state = RightState(self.binop)


class RightState:

    def __init__(self, binop):
        self.binop = binop

    def evaluate(self):
        self.binop.right.evaluate()
        if self.binop.right.is_forward_completed():
            self.binop.state = EndBinOpState(self.binop)


class EndBinOpState:

    def __init__(self, binop):
        self.binop = binop

    def evaluate(self):
        self.binop.operation.evaluate(self.binop.left.eval, self.binop.right.eval)
        self.binop.state = StartBinOpState(self.binop)


class StartBinOpState:

    def __init__(self, binop):
        self.binop = binop

    def evaluate(self):
        self.binop.state = LeftState(self.binop)
        self.binop.state.evaluate()

