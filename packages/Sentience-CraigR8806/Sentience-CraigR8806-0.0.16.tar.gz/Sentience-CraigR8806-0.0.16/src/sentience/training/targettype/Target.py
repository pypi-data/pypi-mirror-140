from abc import abstractmethod
from sentience.training.InputTarget import InputTarget


class Target(InputTarget):


    def __init__(self, name:str):
        super().__init__(name)

    @abstractmethod
    def addValueToTargetList(self, value, target:list):
        pass