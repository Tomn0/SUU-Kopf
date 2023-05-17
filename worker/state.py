class State: # TODO duplicating classes is evil

    def __init__(self, somenumber: int):
        self.somenumber = somenumber # tmp

    def __str__(self) -> str:
        return f'({str(self.somenumber)})'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        # tmp
        return self.somenumber == other.somenumber
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

# creates an initial state instance (with no work done)
def create_initial_state():
    return State(0)

# returns the state with the most work done
def compare_state(state1: State, state2: State):
    return state1 if state1.somenumber >= state2.somenumber else state2