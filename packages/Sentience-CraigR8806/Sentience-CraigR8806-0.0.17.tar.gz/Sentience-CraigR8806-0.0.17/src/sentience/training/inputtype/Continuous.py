from sentience.training.inputtype.Input import Input
import numpy as np



class ContinuousInput(Input):


    def __init__(self, name:str, minValue:np.float32, maxValue:np.float32):
        super().__init__(name)
        self.minValue=minValue
        self.maxValue=maxValue

    def normalizeValue(self, value:np.float32) -> np.float32:
        return np.float32((float(value) - float(self.minValue))/(float(self.maxValue) - float(self.minValue)))


    def addValueToInputList(self, value:np.float32, input:list) -> np.float32:
        input.append(self.normalizeValue(value))