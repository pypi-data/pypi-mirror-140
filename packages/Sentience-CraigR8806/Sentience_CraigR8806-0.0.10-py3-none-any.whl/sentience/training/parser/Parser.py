from abc import ABC, abstractmethod



class Parser(ABC):



    def __init__(self):
        self.delimiters={}
        pass


    @classmethod
    @abstractmethod
    def getParserInstance(cls):
        pass

    @abstractmethod
    def setDelimitersUsingDictionary(self, delimitersPurposeMappedToDelimiter:dict):
        self.delimiters = delimitersPurposeMappedToDelimiter

    @abstractmethod
    def loadTrainingDataAndSpecificationFromDictionaryOfFiles(self, filesPurposeMappedToPath:dict):
        pass

    @abstractmethod
    def loadTrainingDataSpecificationFromFile(self, filesAndPurposeMappedToPath:dict):
        pass