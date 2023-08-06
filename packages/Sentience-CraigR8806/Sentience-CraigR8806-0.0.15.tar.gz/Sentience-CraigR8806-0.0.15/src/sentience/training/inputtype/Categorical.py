from sentience.training.inputtype.Input import Input
import numpy as np



class CategoricalInput(Input):





    def __init__(self, name:str, categoryEnumeration:list):
        super().__init__(name)
        self.categoryEnumeration = categoryEnumeration


    def addValueToInputList(self, value, input:list):
        for category in self.categoryEnumeration:
            if category == value:
                input.append(np.float32(1))
            else:
                input.append(np.float32(0))
        


