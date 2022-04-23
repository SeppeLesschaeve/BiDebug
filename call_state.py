class CallException(Exception):

    def __init__(self):
        super().__init__("Continue evaluation")


class EvalState:

    def __init__(self, call):
        self.call = call

    def evaluate(self):
        self.call.function.evaluate()
        if self.call.function.is_forward_completed():
            self.call.state = EndCallState(self.call)


class EndCallState:

    def __init__(self, call):
        self.call = call

    def evaluate(self):
        self.call.state = StartCallState(self.call)


class StartCallState:

    def __init__(self, call):
        self.call = call

    def evaluate(self):
        self.call.function.initialise(self.call.args)
        self.call.state = EvalState(self.call)
        raise CallException
