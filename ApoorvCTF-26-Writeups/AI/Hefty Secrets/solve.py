"""
Reference solver for the LoRA Merge Weight Visualization CTF challenge.

Steps:
  1. Load the base model and LoRA adapter.
  2. Identify the target layer from adapter key naming convention.
  3. Apply the LoRA update:  W_merged = W + B @ A
  4. Normalize the merged weight matrix to [0, 1].
  5. Visualize and save the result as a grayscale image.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt


def main():
    # ── Load artefacts ─────────────────────────────────────────────────
    base_model = torch.load("base_model.pt", map_location="cpu", weights_only=True)
    adapter = torch.load("lora_adapter.pt", map_location="cpu", weights_only=True)

    print("Base model keys:", list(base_model.keys()))
    print("Adapter keys:  ", list(adapter.keys()))

    # ── Identify target layer ──────────────────────────────────────────
    # Adapter keys follow the pattern  <layer>.lora_A / <layer>.lora_B
    # Extract the layer name prefix from the adapter keys.
    adapter_keys = list(adapter.keys())
    target_layer = adapter_keys[0].rsplit(".lora_", 1)[0]  # e.g. "layer2"
    weight_key = f"{target_layer}.weight"
    print(f"Target layer: {weight_key}")

    # ── Retrieve matrices ──────────────────────────────────────────────
    W = base_model[weight_key]
    lora_A = adapter[f"{target_layer}.lora_A"]
    lora_B = adapter[f"{target_layer}.lora_B"]

    print(f"W shape:      {W.shape}")
    print(f"lora_B shape: {lora_B.shape}")
    print(f"lora_A shape: {lora_A.shape}")

    # ── Apply LoRA merge ───────────────────────────────────────────────
    W_merged = W + lora_B @ lora_A

    # ── Normalize to [0, 1] ────────────────────────────────────────────
    W_np = W_merged.numpy()
    W_min, W_max = W_np.min(), W_np.max()
    W_norm = (W_np - W_min) / (W_max - W_min)

    print(f"Merged weight range: [{W_min:.4f}, {W_max:.4f}]")

    # ── Visualize ──────────────────────────────────────────────────────
    plt.figure(figsize=(6, 6))
    plt.imshow(W_norm, cmap="gray", interpolation="nearest")
    plt.title("Merged Weight Matrix - Flag")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("flag.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Flag image saved to flag.png")


if __name__ == "__main__":
    main()
