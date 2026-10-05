import torch
import numpy as np
from PIL import Image
from torchvision import transforms


CLASS_NAMES = ["COVID-19", "Normal", "Pneumonia"]
CLASS_COLORS = {
    "COVID-19": "#ef4444",
    "Normal": "#22c55e",
    "Pneumonia": "#f59e0b"
}


def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    return transform(image).unsqueeze(0)


def predict(model, image, device="cpu"):
    model.eval()
    input_tensor = preprocess_image(image).to(device)

    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)

    result = {
        "class": CLASS_NAMES[predicted.item()],
        "confidence": confidence.item() * 100,
        "probabilities": {
            CLASS_NAMES[i]: round(prob.item() * 100, 2)
            for i, prob in enumerate(probabilities[0])
        },
        "color": CLASS_COLORS[CLASS_NAMES[predicted.item()]]
    }
    return result
