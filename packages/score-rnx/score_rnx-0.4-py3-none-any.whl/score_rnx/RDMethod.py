from numpy import ndarray


class RDMethod:
    def __init__(self, name, data: ndarray):
        self.name = name
        self.data = data
        self.__score = 0.0
        self.__rnx = []
        self.__state = False

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, new_score):
        self.__score = new_score

    @property
    def rnx(self):
        return self.__rnx

    @rnx.setter
    def rnx(self, new_rnx):
        self.__rnx = new_rnx

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, new_state):
        self.__state = new_state

