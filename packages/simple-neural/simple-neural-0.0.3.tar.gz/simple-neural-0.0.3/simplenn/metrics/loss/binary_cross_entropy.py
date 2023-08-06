import numpy as np
from simplenn.metrics.loss.loss import Loss


class BinaryCrossEntropy(Loss):
    def __call__(self, y_prob, true_labels):
        yc = np.clip(y_prob, 1e-7, 1 - 1e-7)
        eps = np.finfo(np.float32).eps
        # loss_vector = true_labels * np.log(yc + eps) + (1 - true_labels) * np.log(1 - yc + eps)
        loss_vector = -(true_labels * np.log(yc + eps) + (1 - true_labels) * np.log(1 - yc + eps))
        loss_vector = np.mean(loss_vector, axis=-1)

        return np.mean(loss_vector)

    def back(self, z, true_labels):
        zc = np.clip(z, 1e-7, 1 - 1e-7)
        self.zstate = -(true_labels / zc - (1 - true_labels) / (1 - zc)) / len(z[0])
        self.zstate /= len(z)
        return self.zstate
