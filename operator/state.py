class State:

    def __init__(self, somenumber: int):
        self.somenumber = somenumber # tmp

    def __str__(self) -> str:
        return f'({str(self.somenumber)})'
    
    def __repr__(self) -> str:
        return self.__str__()