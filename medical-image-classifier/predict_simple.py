import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from model import ChestXrayClassifier, load_model
from predict import predict, CLASS_NAMES
from PIL import Image
import torch


def simple_predict(image_path):
    device = "cpu"
    model_path = os.path.join("models", "chest_xray_model.pth")

    if not os.path.exists(model_path):
        print("ERROR: Model not found! Train first with: python src/train.py")
        return

    model = load_model(model_path, device=device)
    image = Image.open(image_path).convert("RGB")
    result = predict(model, image, device=device)

    print("\n" + "="*50)
    print("   AI MEDICAL IMAGE CLASSIFIER")
    print("="*50)
    print(f"\n   Prediction:  {result['class']}")
    print(f"   Confidence:  {result['confidence']:.1f}%")
    print(f"\n   All probabilities:")
    for cls, prob in result["probabilities"].items():
        bar = "#" * int(prob / 2)
        print(f"   {cls:12s}: {prob:5.1f}% {bar}")
    print("\n" + "="*50)
    print("   Note: For educational purposes only!")
    print("="*50 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        simple_predict(sys.argv[1])
    else:
        print("Usage: python predict_simple.py <image_path>")
        print("Example: python predict_simple.py data/test/covid/COVID-1.png")
