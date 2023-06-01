class State: # TODO duplicating classes is evil

    def __init__(self, N: int, first_number: int, last_number: int, current_number: int = None):
        self.N = N
        self.first_number = first_number
        self.last_number = last_number
        self.current_number = current_number if current_number is not None else self.first_number

    def __str__(self) -> str:
        return f'N: {str(self.N)} range: [{str(self.first_number)} - {str(self.last_number)}] curr: {str(self.current_number)}'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        return (
            self.first_number == other.first_number
            and self.last_number == other.last_number
        ) 
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

# creates an initial state instance (with no work done)
def create_initial_state():
    return State(0, 100)

# returns the state with the most work done
def is_gte(state1: State, state2: State):
    return state1.current_number >= state2.current_number