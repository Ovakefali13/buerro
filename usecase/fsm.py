from usecase import FinishedException

class StateMachine:
    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []
        self.currentState = None

    def add_state(self, name:str, fun, end_state=False):
        name = name.upper()
        self.handlers[name] = fun

        if end_state:
            self.endStates.append(name)

    def set_start(self, name:str):
        self.startState = name.upper()

    def is_finished(self):
        return self.currentState in self.endStates

    def advance(self, data):
        if not self.endStates:
            raise  Exception("at least one state must be an end_state")
        if self.is_finished():
            raise  FinishedException("advance called on a finished FSM")

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
                raise Exception("new state has not been added",
                    self.currentState)

        ret = handler(data)
        if not isinstance(ret, tuple):
            raise Exception("return of a transition should be a tuple of "
                + "(new_state, data)")

        (new_state, data) = ret
        if new_state is None:
            pass  # leave current state
        elif isinstance(new_state, str):
            new_state = new_state.upper()
            self.currentState = new_state
        else:
            raise Exception("New state should be a string")

        return data

    def get_state(self):
        return self.currentState

    def reset(self):
        self.currentState = None

    def _set_state(self, state:str):
        self.currentState = state.upper()

