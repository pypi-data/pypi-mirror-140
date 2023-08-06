import torch.nn as nn
import torch.nn.functional as F


class SoftCrossEntropyLoss(nn.Module):
    def __init__(self, weights=None):
        super(SoftCrossEntropyLoss, self).__init__()

        self.weights = weights

    def forward(self, y_logits, y_target):
        logsm_y_pred = F.log_softmax(y_logits, dim=1)

        if self.weights is not None:
            y_target = self.weights * y_target

        loss = -(logsm_y_pred * y_target).sum() / (y_target).sum()

        return loss
