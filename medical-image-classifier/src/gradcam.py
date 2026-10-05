import torch
import numpy as np
from PIL import Image
from torchvision import transforms
import torch.nn.functional as F


class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        target_layer.register_forward_hook(self.forward_hook)
        target_layer.register_full_backward_hook(self.backward_hook)

    def forward_hook(self, module, input, output):
        self.activations = output.detach()

    def backward_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor, target_class=None):
        self.model.eval()
        output = self.model(input_tensor)

        if target_class is None:
            target_class = output.argmax(dim=1).item()

        self.model.zero_grad()
        one_hot = torch.zeros_like(output)
        one_hot[0, target_class] = 1
        output.backward(gradient=one_hot, retain_graph=True)

        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        cam = F.interpolate(cam, size=(224, 224), mode='bilinear', align_corners=False)
        return cam.squeeze().numpy()


def _jet_colormap(val):
    """Create a JET-like colormap using numpy (no OpenCV needed)."""
    r = np.clip(1.5 - np.abs(val * 4 - 3), 0, 1)
    g = np.clip(1.5 - np.abs(val * 4 - 2), 0, 1)
    b = np.clip(1.5 - np.abs(val * 4 - 1), 0, 1)
    return np.stack([r, g, b], axis=-1)


def get_gradcam_overlay(image, cam, alpha=0.5):
    cam_uint8 = (cam * 255).astype(np.uint8)
    heatmap_pil = Image.fromarray(cam_uint8).resize(image.size)
    heatmap_arr = np.array(heatmap_pil).astype(np.float32) / 255.0

    colored = _jet_colormap(heatmap_arr)
    heatmap_rgb = (colored * 255).astype(np.uint8)

    img_array = np.array(image).astype(np.float32)
    blended = img_array * (1 - alpha) + heatmap_rgb.astype(np.float32) * alpha
    overlay = np.clip(blended, 0, 255).astype(np.uint8)

    return Image.fromarray(overlay), Image.fromarray(heatmap_rgb)


def generate_gradcam(model, image, device="cpu", target_class=None):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    input_tensor = transform(image).unsqueeze(0).to(device)

    target_layer = model.backbone.layer4[-1]
    gradcam = GradCAM(model, target_layer)
    cam = gradcam.generate(input_tensor, target_class)

    overlay, heatmap = get_gradcam_overlay(image, cam)

    return {
        "overlay": overlay,
        "heatmap": heatmap,
        "cam_raw": cam
    }
