from simplenn.block import Block

import numpy as np


class ReLu(Block):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, block: Block, inference: bool = False):
        x = self.register_block(block, inference)
        output = np.maximum(0, x)
        if inference:
            return output
        self.x = x
        self.output = output
        return self

    def back(self, z):
        self.zstate = z.copy()
        self.zstate[self.x <= 0] = 0
        return self.zstate
