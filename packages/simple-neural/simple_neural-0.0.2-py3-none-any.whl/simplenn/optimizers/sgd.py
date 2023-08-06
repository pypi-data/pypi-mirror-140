from typing import List
from typing import Union

from simplenn.layer import Layer


class SGD:
    def __init__(
        self,
        lr: float = 0.1,
        decay: Union[float, None] = None,
        momentum: Union[float, None] = None,
    ) -> None:
        self.lr = lr
        self.decay = decay
        self.momentum = momentum
        self.iteration = 0

    def get_adjusted_lr(self):
        """Learning rate adjusted by linear decay"""
        lr = self.lr
        if self.decay:
            lr = self.lr / (1 + self.decay * self.iteration)
        return lr

    def _get_momentum(self, layer: Layer):
        if self.momentum is None:
            return 0, 0

        layer._init_momentum()
        return self.momentum * layer.W_momentum, self.momentum * layer.b_momentum

    def _update_momentum(self, layer: Layer, W_update, b_update):
        if self.momentum is None:
            return

        layer.W_momentum = W_update
        layer.b_momentum = b_update

    def learn(self, layers: List[Layer]):
        lr = self.get_adjusted_lr()
        for layer in layers:

            W_momentum, b_momentum = self._get_momentum(layer)

            W_update = W_momentum - (lr * layer.dW)
            b_update = b_momentum - (lr * layer.db)

            layer.W += W_update
            layer.b += b_update

            self._update_momentum(layer, W_update, b_update)

        self.iteration += 1
