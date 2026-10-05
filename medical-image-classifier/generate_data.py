import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def create_synthetic_xray(label, size=(224, 224)):
    img = Image.new("L", size, color=np.random.randint(10, 40))
    draw = ImageDraw.Draw(img)

    cx, cy = size[0] // 2, size[1] // 2

    draw.ellipse([cx-60, cy-80, cx+60, cy+80], fill=np.random.randint(60, 120))
    draw.ellipse([cx-30, cy-20, cx-10, cy+20], fill=np.random.randint(150, 200))
    draw.ellipse([cx+10, cy-20, cx+30, cy+20], fill=np.random.randint(150, 200))

    if label == "covid":
        for _ in range(np.random.randint(3, 8)):
            x = cx + np.random.randint(-40, 40)
            y = cy + np.random.randint(-50, 50)
            r = np.random.randint(3, 10)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=np.random.randint(80, 140))
    elif label == "pneumonia":
        draw.ellipse([cx-50, cy-10, cx+50, cy+40], fill=np.random.randint(100, 160))
        draw.rectangle([cx-20, cy+20, cx+20, cy+60], fill=np.random.randint(90, 150))

    img = img.convert("RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    noise = np.random.normal(0, 10, (size[1], size[0], 3)).astype(np.uint8)
    img = Image.fromarray(np.clip(np.array(img) + noise, 0, 255).astype(np.uint8))
    return img


def generate_dataset(data_dir, train=80, val=20, test=20):
    labels = ["covid", "normal", "pneumonia"]
    splits = {"train": train, "val": val, "test": test}

    for split, count in splits.items():
        for label in labels:
            folder = os.path.join(data_dir, split, label)
            os.makedirs(folder, exist_ok=True)
            for i in range(count):
                img = create_synthetic_xray(label)
                img.save(os.path.join(folder, f"{label}_{i:04d}.png"))
            print(f"  {split}/{label}: {count} images")

    print(f"\nTotal: {(train+val+test)*3} synthetic images created!")


if __name__ == "__main__":
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    print("Generating synthetic chest X-ray dataset...")
    generate_dataset(DATA_DIR, train=80, val=20, test=20)
