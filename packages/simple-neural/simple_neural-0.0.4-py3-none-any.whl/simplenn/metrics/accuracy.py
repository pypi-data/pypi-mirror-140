import numpy as np

THRESHOLD = 0.5


class Accuracy:
    NAME = "accuracy"
    ALIAS = "acc"

    def __call__(self, y_hat, targets, threshold=THRESHOLD):
        if np.size(y_hat) == np.size(np.squeeze(y_hat)) and y_hat.shape[-1] == 1:
            y_hat = (y_hat > threshold) * 1
            return np.mean(targets == y_hat)

        if len(targets.shape) == 2:
            targets = np.argmax(targets, axis=1)
        if len(y_hat.shape) == 2:
            y_hat = np.argmax(y_hat, axis=1)

        return np.mean(targets == y_hat)
