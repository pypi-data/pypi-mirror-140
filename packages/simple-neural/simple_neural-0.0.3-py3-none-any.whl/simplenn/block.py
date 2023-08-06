from abc import ABC
from typing import Union


class Block(ABC):
    """Base building block for neural network components"""

    def __init__(self) -> None:
        self.prev_block: Union[Block, None] = None
        self.next_block: Union[Block, None] = None

    def __call__(self, x):
        """Forward pass"""
        raise NotImplementedError

    def register_block(self, block, inference: bool = False):
        x = block
        # print(block, inference)
        if isinstance(block, Block) and not inference:
            block.next_block = self
            self.prev_block = block
            x = x.output
        return x

    def cleanup(self):
        if hasattr(self, "output"):
            del self.output
        if hasattr(self, "zstate"):
            del self.zstate
        if hasattr(self, "x"):
            del self.x
        if hasattr(self, "dW"):
            del self.dW
        if hasattr(self, "db"):
            del self.db
