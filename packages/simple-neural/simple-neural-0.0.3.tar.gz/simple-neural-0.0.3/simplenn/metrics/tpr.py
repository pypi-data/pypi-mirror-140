import numpy as np

THRESHOLD = 0.5


class TPR:
    NAME = "true_positive_rate"
    ALIAS = "tpr"

    def __call__(self, y_hat, targets, threshold=THRESHOLD):
        y_hat = (y_hat > threshold) * 1
        true_positive = np.equal(y_hat, 1) & np.equal(targets, 1)
        false_negative = np.equal(y_hat, 0) & np.equal(targets, 1)
        eps = np.finfo(np.float32).eps
        return true_positive.sum() / (true_positive.sum() + false_negative.sum() + eps)
