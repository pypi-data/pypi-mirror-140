from sentience.training.targettype.Target import Target
import numpy as np



class CategoricalTarget(Target):


    def __init__(self, name:str, categoryEnumeration:list):
        super().__init__(name)
        self.categoryEnumeration = categoryEnumeration


    def addValueToTargetList(self, value, target:list):
        for category in self.categoryEnumeration:
            if category == value:
                target.append(np.float32(1))
            else:
                target.append(np.float32(0))