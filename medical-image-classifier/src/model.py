import torch
import torch.nn as nn
from torchvision import models


class ChestXrayClassifier(nn.Module):
    def __init__(self, num_classes=3, pretrained=True):
        super(ChestXrayClassifier, self).__init__()

        try:
            self.backbone = models.resnet50(
                weights=models.ResNet50_Weights.DEFAULT if pretrained else None
            )
        except AttributeError:
            self.backbone = models.resnet50(pretrained=pretrained)

        for param in list(self.backbone.parameters())[:-20]:
            param.requires_grad = False

        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


def load_model(model_path, num_classes=3, device="cpu"):
    model = ChestXrayClassifier(num_classes=num_classes, pretrained=False)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model
