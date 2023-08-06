from simplenn.metrics.fpr import FPR
from simplenn.metrics.tpr import TPR

ITERATIONS = 1000


class AucROC:
    NAME = "auc_roc"
    ALIAS = "auc"

    def __call__(self, y_hat, targets):
        auc = 0
        last_tpr = None
        last_fpr = None
        for i in range(ITERATIONS + 1):
            threshold = i / ITERATIONS
            tpr = TPR()(y_hat, targets, threshold)
            fpr = FPR()(y_hat, targets, threshold)

            if last_fpr is None:
                last_tpr = tpr
                last_fpr = fpr
                continue

            rectangle_area = (last_fpr - fpr) * last_tpr
            auc += rectangle_area
            last_tpr = tpr
            last_fpr = fpr

        return auc
