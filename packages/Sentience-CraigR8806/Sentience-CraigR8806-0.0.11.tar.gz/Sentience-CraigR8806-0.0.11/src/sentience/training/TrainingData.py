import time
from sentience.training.TrainingDataSpecification import TrainingDataSpecification
from sentience.training.parser.Parser import Parser
from sentience.net.Net import Net
import numpy as np


class TrainingData:

    def __init__(self, trainingDataSpecification:TrainingDataSpecification, trainingData:list, net:Net):
        self.trainingDataSpecification = trainingDataSpecification
        self.trainingData = trainingData
        self.net = net



    @classmethod
    def fromFileWithNewNet(cls, filesPurposeMappedToPath:dict, parser:Parser, numberOfHiddenNodesPerHiddenLayer = None):
        specification, trainingData = parser.loadTrainingDataAndSpecificationFromDictionaryOfFiles(filesPurposeMappedToPath)
        if numberOfHiddenNodesPerHiddenLayer == None:
            numberOfHiddenNodesPerHiddenLayer=[int(np.ceil(specification.getNumberOfInputNodes() * .666 + specification.getNumberOfTargetNodes()))]
        
        print("numberOfHiddenLayerNodes " + str(numberOfHiddenNodesPerHiddenLayer[0]))
        print("Number of Input Nodes: " + str(specification.getNumberOfInputNodes()))
        print("Number of Target Nodes: " + str(specification.getNumberOfTargetNodes()))
        net = Net.randomWeightAndBiasNet(specification.getNumberOfInputNodes(), specification.getNumberOfTargetNodes(), numberOfHiddenNodesPerHiddenLayer)
        return cls(trainingDataSpecification=specification, trainingData=trainingData, net=net)

    @classmethod
    def fromFileWithSavedNet(cls, filesPurposeMappedToPath:dict, parser:Parser, netPath:str):
        specification, trainingData = parser.loadTrainingDataAndSpecificationFromDictionaryOfFiles(filesPurposeMappedToPath)
        net = Net.loadNetFromFile(netPath)
        return cls(trainingDataSpecification=specification, trainingData=trainingData, net=net)


    def trainOnFullSet(self, learningRate:np.float32, biasLearningRate:np.float32, numberOfIterations:int, lazyLoad=False):
        inputs=[]
        targets=[]
        if not lazyLoad:
            inputs, targets = self._normalizeTrainingData()

        for i in range(numberOfIterations):
            for i in range(len(inputs)):
                input, target = self.getNormalizedTrainingDataItem(i, inputs, targets, lazyLoad)
                self.net.train(learningRate, biasLearningRate, input, target)

    def trainOnRandomSelectionFromSet(self, learningRate:np.float32, biasLearningRate:np.float32, numberOfIterations:int, numberOfRandomSamples:int, lazyLoad=False):
        inputs=[]
        targets=[]
        if not lazyLoad:
            loading_start = time.time()
            inputs, targets = self._normalizeTrainingData()
            loading_stop = time.time()
            print('...Begin training output...')
            print("loading time: " + str(loading_stop - loading_start) + " seconds")
        start=time.time()
        for i in range(numberOfIterations):
            allTrainingIndicies=[index for index in range(len(self.trainingData))]
            for j in range(numberOfRandomSamples):
                index = allTrainingIndicies[np.random.randint(0, len(allTrainingIndicies))]
                allTrainingIndicies.remove(index)
                input, target = self.getNormalizedTrainingDataItem(index, inputs, targets, lazyLoad)
                self.net.train(learningRate, biasLearningRate, input, target)
        stop=time.time()
        print("processing time: " + str(stop - start) + " seconds")
        print('...End training output...')
        

    def trainOnFullSetRandomly(self, learningRate:np.float32, biasLearningRate:np.float32, numberOfIterations:int, lazyLoad=False):
        self.trainOnRandomSelectionFromSet(learningRate, biasLearningRate, numberOfIterations, len(self.trainingData), lazyLoad)

    def testNet(self, dataIndex:int):
        inputs, targets = self._normalizeTrainingData()
        return (self.net.forwardProp(inputs[dataIndex]), targets[dataIndex])

    def testNetWithRandomSample(self, numberOfSamples:int, threshhold=0.01, lazyLoad=False):
        inputs=[]
        targets=[]
        if not lazyLoad:
            loading_start=time.time()
            inputs, targets = self._normalizeTrainingData()
            loading_stop=time.time()
            print('...Begin testing output...')
            print("loading time: " + str(loading_stop - loading_start) + " seconds")

        numberCorrect=0
        allTrainingIndicies=[index for index in range(len(self.trainingData))]
        start=time.time()
        for i in range(numberOfSamples):
            index = allTrainingIndicies[np.random.randint(0, len(allTrainingIndicies))]
            allTrainingIndicies.remove(index)
            input, target = self.getNormalizedTrainingDataItem(index, inputs, targets, lazyLoad)
            output=self.net.forwardProp(input)
            correct = True
            # print(str(targets[index]) + "  -  " + str(output))
            for j in range(len(target)):
                delta = abs(target[j] - output[j])
                # print(str(delta) + " " + str(threshhold) + " " + str(delta >= threshhold))
                if delta >= threshhold:
                    correct=False
            if correct:
                numberCorrect+=1
        stop=time.time()
        print("processing time: " + str(stop - start) + " seconds")
        print("Number correct: " + str(numberCorrect))
        print('...End testing output...')
        return str(100*(numberCorrect/numberOfSamples)) + "% Accuracy"

    def testNetWithFullSet(self, threshhold=0.01, lazyLoad=False):
        return self.testNetWithRandomSample(len(self.trainingData), threshhold, lazyLoad)


    def getNormalizedTrainingDataItem(self, index, inputs, targets, lazyLoad):
        if lazyLoad:
            return self._normalizeOneTrainingItem(index)
        else:
            return (inputs[index], targets[index])


    def _normalizeTrainingData(self):
        inputs=[]
        targets=[]
        for i  in range(len(self.trainingData)):
            input, target = self._normalizeOneTrainingItem(i)
            inputs.append(input)
            targets.append(target)
        return (inputs, targets)

    def _normalizeOneTrainingItem(self, index):
        input=[]
        target=[]
        data=self.trainingData[index]
        for i in range(len(data['input'])):
            self.trainingDataSpecification.getFeatures()[i].addValueToInputList(data['input'][i], input)
        for i in range(len(data['target'])):
            self.trainingDataSpecification.getTargets()[i].addValueToTargetList(data['target'][i], target)
        return (input, target)

    def saveNetToFile(self, path:str):
        self.net.exportNetToFile(path)