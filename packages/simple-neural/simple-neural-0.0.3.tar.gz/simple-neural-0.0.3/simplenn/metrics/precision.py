import numpy as np

THRESHOLD = 0.5


class Precision:
    NAME = "precision"
    ALIAS = "pr"

    def __call__(self, y_hat, targets, threshold=THRESHOLD):
        y_hat = (y_hat > threshold) * 1
        true_positive = np.equal(y_hat, 1) & np.equal(targets, 1)
        false_positive = np.equal(y_hat, 1) & np.equal(targets, 0)
        eps = np.finfo(np.float32).eps
        return true_positive.sum() / (true_positive.sum() + false_positive.sum() + eps)
