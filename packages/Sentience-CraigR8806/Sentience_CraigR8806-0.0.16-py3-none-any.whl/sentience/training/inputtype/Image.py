from sentience.training.inputtype.Input import Input
import numpy as np

class ImageInput(Input):



    def __init__(self, name:str, maxPixelValue:int):
        super().__init__(name)
        self.maxPixelValue=maxPixelValue


    def addValueToInputList(self, value, input):
        input.extend([self.normalizeValue(pixel, 0, self.maxPixelValue) for pixel in value])

        
    def normalizeValue(self, value, min, max):
        return (float(value) - float(min))/(float(max) - float(min))

