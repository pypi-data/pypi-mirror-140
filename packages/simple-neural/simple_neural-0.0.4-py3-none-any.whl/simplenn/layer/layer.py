from simplenn.block import Block

import numpy as np


class Layer(Block):
    def __init__(self, input_shape, output_shape, alpha=0.01, W_l1=0, W_l2=0, b_l1=0, b_l2=0) -> None:
        super().__init__()
        self.W = alpha * np.random.randn(input_shape, output_shape)
        self.b = np.zeros((1, output_shape))
        self.dW: np.ndarray = np.array(list())
        self.db: np.ndarray = np.array(list())
        self.W_l1 = W_l1
        self.W_l2 = W_l2
        self.b_l1 = b_l1
        self.b_l2 = b_l2
        self.momentum_initialized = False
        self.cache_initialized = False
        self.frozen = False

    def _init_momentum(self):
        if not self.momentum_initialized:
            self.momentum_initialized = True
            self.W_momentum: np.ndarray = np.zeros_like(self.W)
            self.b_momentum: np.ndarray = np.zeros_like(self.b)

    def _init_cache(self):
        if not self.cache_initialized:
            self.cache_initialized = True
            self.W_cache: np.ndarray = np.zeros_like(self.W)
            self.b_cache: np.ndarray = np.zeros_like(self.b)

    def freeze(self) -> None:
        self.frozen = True
