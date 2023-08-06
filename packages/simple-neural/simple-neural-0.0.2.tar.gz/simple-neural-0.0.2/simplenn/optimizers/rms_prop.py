from typing import List
from typing import Union

import numpy as np
from simplenn.layer import Layer


class RMSProp:
    """
    Root Mean Square Propagation
    Adaptive gradient -> learning rate for every parameter with a running average (momentum)
    """

    def __init__(self, lr: float = 0.1, decay: Union[float, None] = None, eps: Union[float, None] = 1e-7, rho: float = 0.7) -> None:
        self.lr = lr
        self.decay = decay
        self.eps = eps
        self.rho = rho
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
        layer.W_cache = self.rho * layer.W_cache + (1 - self.rho) * layer.dW**2
        layer.b_cache = self.rho * layer.b_cache + (1 - self.rho) * layer.db**2

    def learn(self, layers: List[Layer]):
        lr = self.get_adjusted_lr()
        for layer in layers:

            W_cache, b_cache = self._get_cache(layer)

            W_update = -(lr * layer.dW) / W_cache
            b_update = -(lr * layer.db) / b_cache

            layer.W += W_update
            layer.b += b_update

        self.iteration += 1
