import numpy as np
from simplenn.metrics.loss.loss import Loss


class MeanSquaredError(Loss):
    NAME = "mean_squared_error"
    ALIAS = "mse"

    def __call__(self, prediction, targets):
        loss_vector = np.mean((targets - prediction) ** 2, axis=-1)
        return np.mean(loss_vector)

    def back(self, z, targets):
        self.zstate = -2 * (targets - z) / len(z[0])
        self.zstate /= len(z)
        return self.zstate
