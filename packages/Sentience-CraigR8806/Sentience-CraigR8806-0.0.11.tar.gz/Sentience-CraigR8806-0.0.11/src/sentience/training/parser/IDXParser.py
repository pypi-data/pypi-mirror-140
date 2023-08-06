from sentience.training.parser.Parser import Parser
from sentience.training.TrainingDataSpecification import TrainingDataSpecification
from sentience.training.targettype.Categorical import CategoricalTarget
from sentience.training.inputtype.Image import ImageInput


class IDXParser(Parser):


    _INSTANCE = None


    def __init__(self):
        super().__init__()
        self.delimiters = delimiters={'field_delimiter':':', 'value_delimiter':","}
    
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
        specification = TrainingDataSpecification.fromFile(filesPurposeMappedToPath, self)
        trainingData=[]
        imgDataFilePath=filesPurposeMappedToPath['dataPath']
        imgLabelsFilePath=filesPurposeMappedToPath['labelPath']
        with open(imgDataFilePath, 'rb') as dataFile, open(imgLabelsFilePath, 'rb') as lblFile:
            ibytesHeader=dataFile.read1(16)
            lbytesHeader=lblFile.read1(8)
            numberOfImages = int.from_bytes(ibytesHeader[4:8], byteorder="big")
            rows = int.from_bytes(ibytesHeader[8:12], byteorder="big")
            columns = int.from_bytes(ibytesHeader[12:], byteorder="big")
            if numberOfImages != int.from_bytes(lbytesHeader[4:], byteorder="big"):
                raise ValueError("Provided Image files don't appear to correspond to the same images")
            bytesPerImage=rows*columns
            for i in range(numberOfImages):
                input = []
                target = []
                pixelData=[b for b in dataFile.read1(bytesPerImage)]
                targetValue=int.from_bytes(lblFile.read1(1), byteorder="big")
                input.append(pixelData)
                target.append(targetValue)
                trainingData.append({"input":input, "target": target})
        return (specification, trainingData)
                
                

            
        

    def loadTrainingDataSpecificationFromFile(self, filesAndPurposeMappedToPath: dict):
        speicificationPath = filesAndPurposeMappedToPath['specificationPath']
        features=[]
        targets=[]
        numberOfInputNodes=0
        numberOfTargetNodes=0
        with open(speicificationPath, 'r') as file:
            lines = file.readlines()
            fieldNumber=0
            for line in lines:
                fields=line.removesuffix("\n").strip().split(self.delimiters['field_delimiter'])
                name = fields[1]
                if fields[0] == "input":
                    if fields[2] == "image":
                        rows=int(fields[5])
                        columns=int(fields[6])
                        maxPixelValue=int(fields[4])
                        features.append(ImageInput(name, maxPixelValue))
                        numberOfInputNodes+=rows*columns
                elif fields[0] == "target":
                    if fields[2] == "categorical":
                        categories=[value.strip() for value in fields[3].split(self.delimiters['value_delimiter'])]
                        targets.append(CategoricalTarget(name, categories))
                        numberOfTargetNodes+=len(categories)
        return TrainingDataSpecification(features=features, targets=targets, numberOfInputNodes=numberOfInputNodes, numberOfTargetNodes=numberOfTargetNodes)
    