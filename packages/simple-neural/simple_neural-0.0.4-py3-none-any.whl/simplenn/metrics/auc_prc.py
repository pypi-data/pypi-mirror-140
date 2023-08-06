from simplenn.metrics.precision import Precision
from simplenn.metrics.tpr import TPR

ITERATIONS = 1000


class AucPRC:
    NAME = "auc_prc"
    ALIAS = "prc"

    def __call__(self, y_hat, targets):
        auc = 0
        last_tpr = None
        last_precision = None
        for i in range(ITERATIONS + 1):
            threshold = i / ITERATIONS
            tpr = TPR()(y_hat, targets, threshold)
            precision = Precision()(y_hat, targets, threshold)

            if last_precision is None:
                last_tpr = tpr
                last_precision = precision
                continue

            rectangle_area = (last_tpr - tpr) * last_precision
            auc += rectangle_area
            last_tpr = tpr
            last_precision = precision

        return auc
