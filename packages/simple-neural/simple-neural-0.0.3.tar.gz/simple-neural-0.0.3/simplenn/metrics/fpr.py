import numpy as np

THRESHOLD = 0.5


class FPR:
    NAME = "false_positive_rate"
    ALIAS = "fpr"

    def __call__(self, y_hat, targets, threshold=THRESHOLD):
        y_hat = (y_hat > threshold) * 1
        true_negative = np.equal(y_hat, 0) & np.equal(targets, 0)
        false_positive = np.equal(y_hat, 1) & np.equal(targets, 0)
        eps = np.finfo(np.float32).eps
        return false_positive.sum() / (false_positive.sum() + true_negative.sum() + eps)
