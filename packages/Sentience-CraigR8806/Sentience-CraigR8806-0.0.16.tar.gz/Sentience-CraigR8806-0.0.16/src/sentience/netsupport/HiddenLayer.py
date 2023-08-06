from parallellinear.datatypes.Matrix import Matrix
from parallellinear.datatypes.Vector import Vector
from sentience.netsupport.Layer import Layer

class HiddenLayer(Layer):
    
    
    

    def __init__(self, data:Vector, weights:Matrix, biases:Vector):
        super().__init__(data)
        self.weights = weights
        self.biases = biases

    @classmethod
    def randomHiddenLayer(cls, numberOfNodes, previousLayersNumberOfNodes):
        return cls(data=Vector.zeros(numberOfNodes), 
            weights=Matrix.random(previousLayersNumberOfNodes, numberOfNodes, 
            random_low=-1), biases=Vector.random(numberOfNodes))

