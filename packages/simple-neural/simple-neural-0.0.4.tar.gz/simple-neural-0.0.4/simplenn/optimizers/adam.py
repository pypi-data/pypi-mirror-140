from simplenn.layer import Layer
from typing import List
from typing import Union

import numpy as np


class Adam:
    """
    Adaptive Momentum
        - Uses running average of gradients (momentum) (as SGD)
            proportion of current gradient in update is set with b1
        - Per-parameter learning rate with cache (as RMSProp)
        - bias correction terms to cache and momentum to account
            controlled with b2

    """

    def __init__(self, lr: float = 0.1, decay: Union[float, None] = None, eps: Union[float, None] = 1e-7, b1: float = 0.9, b2: float = 0.999) -> None:
        self.lr = lr
        self.decay = decay
        self.eps = eps
        self.b1 = b1
        self.b2 = b2
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

        W_cache = np.sqrt(layer.W_cache / (1 - self.b2 ** (self.iteration + 1))) + self.eps
        b_cache = np.sqrt(layer.b_cache / (1 - self.b2 ** (self.iteration + 1))) + self.eps

        return W_cache, b_cache

    def _update_cache(self, layer: Layer):
        """Same as RMSProp. b2 is Rho"""
        layer.W_cache = self.b2 * layer.W_cache + (1 - self.b2) * layer.dW**2
        layer.b_cache = self.b2 * layer.b_cache + (1 - self.b2) * layer.db**2

    def _get_momentum(self, layer: Layer):
        layer._init_momentum()
        self._update_momentum(layer)

        W_momentum = layer.W_momentum / (1 - self.b1 ** (self.iteration + 1))
        b_momentum = layer.b_momentum / (1 - self.b1 ** (self.iteration + 1))

        return W_momentum, b_momentum

    def _update_momentum(self, layer: Layer):
        """update with current gradients. b1 is momentum coefficient"""
        layer.W_momentum = self.b1 * layer.W_momentum + (1 - self.b1) * layer.dW
        layer.b_momentum = self.b1 * layer.b_momentum + (1 - self.b1) * layer.db

    def step(self, layers: List[Layer]):
        lr = self.get_adjusted_lr()
        for layer in layers:

            W_cache, b_cache = self._get_cache(layer)
            W_momentum, b_momentum = self._get_momentum(layer)

            W_update = -(lr * W_momentum) / W_cache
            b_update = -(lr * b_momentum) / b_cache

            layer.W += W_update
            layer.b += b_update

        self.iteration += 1
