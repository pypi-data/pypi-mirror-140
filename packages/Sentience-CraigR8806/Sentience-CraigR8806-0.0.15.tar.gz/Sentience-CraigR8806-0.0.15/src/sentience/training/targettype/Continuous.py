from sentience.training.targettype.Target import Target
import numpy as np



class ContinuousTarget(Target):


    def __init__(self, name:str, min:np.float32, max:np.float32):
        super().__init__(name)
        self.min = min
        self.max = max

    def addValueToTargetList(self, value:np.float32, target:list):
        target.append(self.normalizeValue(value))


    def normalizeValue(self, value:np.float32) -> np.float32:
        return np.float32((value - self.minValue)/(self.maxValue - self.minValue))
