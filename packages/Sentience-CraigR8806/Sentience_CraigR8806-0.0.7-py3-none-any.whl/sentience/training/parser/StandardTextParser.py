from sentience.training.parser.Parser import Parser
from sentience.training.TrainingDataSpecification import TrainingDataSpecification
from sentience.training.inputtype.Categorical import CategoricalInput
from sentience.training.inputtype.Continuous import ContinuousInput
from sentience.training.targettype.Categorical import CategoricalTarget
from sentience.training.targettype.Continuous import ContinuousTarget
import numpy as np


class StandardTextParser(Parser):

    _INSTANCE = None


    def __init__(self):
        super().__init__()
        self.delimiters = delimiters={'data_delimiter':",", 'field_delimiter':':', 'value_delimiter':","}

    
    def __new__(cls):
        if cls._INSTANCE == None:
            cls._INSTANCE = object.__new__(cls)
        return cls._INSTANCE

    @classmethod
    def getParserInstance(cls):
        return cls()

    def setDelimitersUsingDictionary(self, delimitersPurposeMappedToDelimiter: dict):
        super().setDelimitersUsingDictionary(delimitersPurposeMappedToDelimiter)

    def loadTrainingDataAndSpecificationFromDictionaryOfFiles(self, filesPurposeMappedToPath: dict):
        dataPath=filesPurposeMappedToPath['dataPath']
        specification = TrainingDataSpecification.fromFile(filesPurposeMappedToPath, self)
        trainingData = []
        with open(dataPath, 'r') as file:
            for line in file.readlines():
                input = []
                target = []
                values=[val.strip() for val in line.removesuffix("\n").split(self.delimiters['data_delimiter'])]
                for i in range(len(specification.getFeatures())):
                    input.append(values[i])
                for i in range(len(specification.getFeatures()), len(values)):
                    target.append(values[i])
                trainingData.append({"input":input, "target": target})

        return (specification, trainingData)


    def loadTrainingDataSpecificationFromFile(self, filesAndPurposeMappedToPath: dict) -> TrainingDataSpecification:
        dataPath=filesAndPurposeMappedToPath['dataPath']
        specificationPath=filesAndPurposeMappedToPath['specificationPath']
        features = []
        targets = []
        datalines=[]
        numberOfInputNodes=0
        numberOfTargetNodes=0
        with open(dataPath, 'r') as file:
            datalines=[line.split(self.delimiters['data_delimiter']) for line in file.readlines()]
        with open(specificationPath, 'r') as file:
            lines=file.readlines()
            fieldNumber=0
            for line in lines:
                fields=line.removesuffix("\n").strip().split(self.delimiters['field_delimiter'])
                name=fields[1]
                if fields[0] == "input":
                    if fields[2] == "continuous":
                        min=np.min([np.float32(dataline[fieldNumber]) for dataline in datalines])
                        max=np.max([np.float32(dataline[fieldNumber]) for dataline in datalines])
                        features.append(ContinuousInput(name, min, max))
                        numberOfInputNodes+=1
                    elif fields[2] == "categorical":
                        categories=[value.strip() for value in fields[3].split(self.delimiters['value_delimiter'])]
                        features.append(CategoricalInput(name, categories))
                        numberOfInputNodes+=len(categories)
                elif fields[0] == "target":
                    if fields[2] == "continuous":
                        min=np.min([np.float32(dataline[fieldNumber]) for dataline in datalines])
                        max=np.max([np.float32(dataline[fieldNumber]) for dataline in datalines])
                        targets.append(ContinuousTarget(name, min, max))
                        numberOfTargetNodes+=1
                    elif fields[2] == "categorical":
                        categories=[value.strip() for value in fields[3].split(self.delimiters['value_delimiter'])]
                        targets.append(CategoricalTarget(name, categories))
                        numberOfTargetNodes+=len(categories)
                fieldNumber+=1
        return TrainingDataSpecification(features=features, targets=targets, numberOfInputNodes=numberOfInputNodes, numberOfTargetNodes=numberOfTargetNodes)
