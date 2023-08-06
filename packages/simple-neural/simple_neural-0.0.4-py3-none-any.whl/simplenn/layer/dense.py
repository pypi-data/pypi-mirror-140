from simplenn.block import Block
from typing import Union

import numpy as np

from .layer import Layer


class Dense(Layer):
    def __call__(self, block: Union[Block, np.ndarray], inference: bool = False):
        x = self.register_block(block, inference)
        output = np.dot(x, self.W) + self.b

        if inference:
            return output

        self.x = x
        self.output = output
        return self

    def back(self, z):
        # Gradients on parameters
        self.dW = np.dot(self.x.T, z)
        self.db = np.sum(z, axis=0, keepdims=True)

        if self.W_l1 > 0:
            dL1 = np.ones_like(self.W)
            dL1[self.W < 0] = -1
            self.dW += self.W_l1 * dL1
        if self.b_l1 > 0:
            dL1 = np.ones_like(self.b)
            dL1[self.b < 0] = -1
            self.db += self.b_l1 * dL1
        if self.W_l2 > 0:
            self.dW += 2 * self.W_l2 * self.W
        if self.b_l2 > 0:
            self.db += 2 * self.b_l2 * self.b

        # Gradient on values
        self.zstate = np.dot(z, self.W.T)
        return self.zstate
