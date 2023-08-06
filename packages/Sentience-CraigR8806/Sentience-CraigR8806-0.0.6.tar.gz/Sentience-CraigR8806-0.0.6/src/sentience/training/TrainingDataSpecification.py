from sentience.training.parser.Parser import Parser
from sentience.training.inputtype.Categorical import CategoricalInput
from sentience.training.inputtype.Continuous import ContinuousInput
from sentience.training.inputtype.Input import Input
from sentience.training.targettype.Categorical import CategoricalTarget
from sentience.training.targettype.Continuous import ContinuousTarget
from sentience.training.targettype.Target import Target
import numpy as np




class TrainingDataSpecification:


    def __init__(self, features:list, targets:list, numberOfInputNodes:int, numberOfTargetNodes:int):
        self.features = features
        self.targets = targets
        self.numberOfInputNodes = numberOfInputNodes
        self.numberOfTargetNodes = numberOfTargetNodes




    @classmethod
    def fromFile(cls, filesDictionary:dict, parser:Parser):
        return parser.loadTrainingDataSpecificationFromFile(filesDictionary)
                


    def getFeatures(self):
        return self.features

    def getTargets(self):
        return self.targets

    def getNumberOfInputNodes(self):
        return self.numberOfInputNodes

    def getNumberOfTargetNodes(self):
        return self.numberOfTargetNodes
