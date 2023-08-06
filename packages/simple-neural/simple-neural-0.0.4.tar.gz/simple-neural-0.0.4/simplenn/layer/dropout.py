from simplenn.block import Block
from typing import Union

import numpy as np


class Dropout(Block):
    def __init__(self, rate) -> None:
        super().__init__()
        self.rate = 1 - rate

    def __call__(self, block: Union[Block, np.ndarray], inference: bool = False):
        x = self.register_block(block, inference)

        if inference:
            return x

        self.scaled_boolean_filter = np.random.binomial(1, self.rate, size=x.shape) / self.rate
        self.output = x * self.scaled_boolean_filter
        return self

    def back(self, z):
        self.zstate = z * self.scaled_boolean_filter
        return self.zstate
