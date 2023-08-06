import numpy as np
from simplenn.block import Block


class SoftMax(Block):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, block: Block, inference: bool = False):
        x = self.register_block(block, inference)
        exp = np.exp(x - np.max(x, axis=1, keepdims=True))
        output = exp / np.sum(exp, axis=1, keepdims=True)

        if inference:
            return output

        self.output = output
        return self.output

    def back(self, z):
        self.zstate = np.empty_like(z)
        for i, (term_output, term_z) in enumerate(zip(self.output, z)):
            term_output = term_output.reshape(-1, 1)  # flatten
            jacobian = np.diagflat(term_output) - np.dot(term_output, term_output.T)
            self.zstate[i] = np.dot(jacobian, term_z)

        return self.zstate


class SoftMaxLoss(Block):
    def __init__(self, loss) -> None:
        super().__init__()
        self.loss = loss
        self.activation = SoftMax()

    def __call__(self, block, targets=None, inference: bool = False):
        x = self.register_block(block)
        output = self.activation(x)
        if inference:
            return output
        self.output = self.activation(x)
        return self.output, self.loss(self.output, targets)

    def back(self, z, targets):
        n = len(z)
        if len(targets.shape) == 2:
            targets = np.argmax(targets, axis=1)

        self.zstate = z.copy()
        self.zstate[range(n), targets] -= 1
        self.zstate /= n

        return self.zstate
