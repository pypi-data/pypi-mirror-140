from parallellinear.datatypes.Vector import Vector


class Layer():


    def __init__(self, data:Vector):
        self.nodeValues = data
        self.weights = None
        self.biases = None

    @classmethod
    def randomLayer(cls, numberOfNodes):
        return cls(data=Vector(numberOfNodes, random=True))

    def getNodes(self):
        return self.nodeValues

    def getNode(self, index):
        return self.nodeValues[index]

    def setNodes(self, nodes):
        self.nodeValues = nodes

    def setNodeValueAtIndex(self, index, value):
        self.nodeValues.setAtPos(index, value)



    def getWeights(self):
        return self.weights

    def getBiases(self):
        return self.biases

    def setWeightAtRowColumn(self, row, column, value):
        self.weights.setAtPos(row, column, value)

    def setBiasAtIndex(self, index, value):
        self.biases.setAtPos(index, value)

    def getNumberOfNodes(self):
        return len(self.nodeValues)


