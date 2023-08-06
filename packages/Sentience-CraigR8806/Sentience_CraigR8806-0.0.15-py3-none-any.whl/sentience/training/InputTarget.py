from abc import ABC, abstractmethod


class InputTarget(ABC):



    def __init__(self, name:str):
        self.name = name



    def getName(self):
        return self.name