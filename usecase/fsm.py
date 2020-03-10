
class StateMachine:
    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []
        self.currentState = None
        self.finished = False

    def add_state(self, name:str, fun, end_state=False):
        name = name.upper()
        self.handlers[name] = fun

        if end_state:
            self.endStates.append(name)

    def set_start(self, name:str):
        self.startState = name.upper()

    def advance(self, data):
        if not self.endStates:
            raise  Exception("at least one state must be an end_state")
        if self.finished:
            raise Exception("advance called on finished machine")

        handler = None
        if not self.currentState:
            try:
                handler = self.handlers[self.startState]
            except:
                raise Exception("must call .set_start() before advance")
        else:
            try:
                handler = self.handlers[self.currentState]
            except:
                raise Exception("new state has not been added")

        ret = handler(data)
        if not isinstance(ret, tuple):
            raise Exception("return of a transition should be a tuple of "
                + "(new_state, data)")
        (new_state, data) = ret
        new_state = new_state.upper()

        if new_state in self.endStates:
            self.finished = True

        self.currentState = new_state

        return data

    def get_state(self):
        return self.currentState

    def reset(self):
        self.currentState = None
        self.finished = False



