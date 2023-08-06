import numpy as np
from simplenn.block import Block


class Sigmoid(Block):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, block, inference: bool = False):
        x = self.register_block(block, inference)
        output = 1 / (1 + np.exp(-x))

        if inference:
            return output
        self.output = output
        return self.output

    def back(self, z):
        # derivative from sigmoid function
        self.zstate = z * (1 - self.output) * self.output
        return self.zstate


class SigmoidLoss(Block):
    def __init__(self, loss) -> None:
        super().__init__()
        self.loss = loss
        self.activation = Sigmoid()

    def __call__(self, block, targets=None, inference: bool = False):
        x = self.register_block(block)
        output = self.activation(x)
        if inference:
            return output
        self.output = output
        return self.output, self.loss(self.output, targets)

    def back(self, z, targets):
        z = self.loss.back(z, targets)
        self.zstate = self.activation.back(z)
        return self.zstate
