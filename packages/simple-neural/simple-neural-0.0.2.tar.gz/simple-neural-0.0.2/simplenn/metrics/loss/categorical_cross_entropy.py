import numpy as np
from simplenn.metrics.loss.loss import Loss


class CategoricalCrossEntropy(Loss):
    def __call__(self, softmax_vector, true_labels):
        yc = np.clip(softmax_vector, 1e-7, 1 - 1e-7)
        if len(true_labels.shape) == 1:
            # Only if categorical labels
            loss_vector = yc[range(yc.shape[0]), true_labels]
        elif len(true_labels.shape) == 2:
            # Only if one-hot labels
            loss_vector = np.sum(yc * true_labels, axis=1)
        # return 10
        return np.mean(-np.log(loss_vector + np.finfo(np.float32).eps))

    def back(self, z, true_labels):
        if len(true_labels.shape) == 1:
            # OHE
            y_true = np.eye(true_labels.shape[1])[true_labels]
        self.zstate = -y_true / z
        self.zstate /= len(z)
        return self.zstate
