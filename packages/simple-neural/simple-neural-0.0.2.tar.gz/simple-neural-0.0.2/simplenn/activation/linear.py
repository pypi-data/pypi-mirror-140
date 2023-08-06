from simplenn.block import Block


class Linear(Block):
    """Pass through Block"""

    def __init__(self) -> None:
        super().__init__()

    def __call__(self, block: Block, inference: bool = False):
        x = self.register_block(block, inference)
        output = x

        if inference:
            return output

        self.output = output
        return self.output

    def back(self, z):
        self.zstate = z.copy()
        return self.zstate


class LinearLoss(Block):
    def __init__(self, loss) -> None:
        super().__init__()
        self.loss = loss
        self.activation = Linear()

    def __call__(self, block, targets=None, inference: bool = False):
        x = self.register_block(block)
        output = self.activation(x)
        if inference:
            return output
        self.output = self.activation(x)
        return self.output, self.loss(self.output, targets)

    def back(self, z, targets):
        z = self.loss.back(z, targets)
        self.zstate = self.activation.back(z)
        return self.zstate
