from simplenn.layer import Layer
from typing import List
from typing import Union

import numpy as np


class AdaGrad:
    """Adaptive gradient -> learning rate for every parameter"""

    def __init__(
        self,
        lr: float = 0.1,
        decay: Union[float, None] = None,
        eps: Union[float, None] = 1e-7,
    ) -> None:
        self.lr = lr
        self.decay = decay
        self.eps = eps
        self.iteration = 0

    def get_adjusted_lr(self):
        """Learning rate adjusted by linear decay"""
        lr = self.lr
        if self.decay:
            lr = self.lr / (1 + self.decay * self.iteration)
        return lr

    def _get_cache(self, layer: Layer):
        layer._init_cache()
        self._update_cache(layer)

        W_cache = np.sqrt(layer.W_cache) + self.eps
        b_cache = np.sqrt(layer.b_cache) + self.eps
        return W_cache, b_cache

    def _update_cache(self, layer: Layer):
        layer.W_cache += layer.dW**2
        layer.b_cache += layer.db**2

    def step(self, layers: List[Layer]):
        lr = self.get_adjusted_lr()
        for layer in layers:

            W_cache, b_cache = self._get_cache(layer)

            W_update = -(lr * layer.dW) / W_cache
            b_update = -(lr * layer.db) / b_cache

            layer.W += W_update
            layer.b += b_update

        self.iteration += 1
