from simplenn.metrics.loss.loss import Loss

import numpy as np


class MeanAbsoluteError(Loss):
    NAME = "mean_absolute_error"
    ALIAS = "mae"

    def __call__(self, prediction, targets):
        loss_vector = np.mean(np.abs(targets - prediction), axis=-1)
        return np.mean(loss_vector)

    def back(self, z, targets):
        self.zstate = np.sign(targets - z) / len(z[0])
        self.zstate /= len(z)
        return self.zstate
