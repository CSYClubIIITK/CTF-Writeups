# Hefty Secrets

## Description

Two files. One network. Something's weighing it down.

You're handed a base model and an adapter. Alone, they're meaningless. Together... well, that's for you to figure out.

Find the flag.

- **Author**: Apoorv
- **Flag**: `apoorvctf{l0r4_m3rg3}`

**Category**: AI/ML

---

## Writeup

### Challenge Overview

We are given two PyTorch files: `base_model.pt` (a neural network state dictionary) and `lora_adapter.pt` (a LoRA adapter). The flag is hidden inside the model weights and only becomes visible after properly merging the adapter into the base model and visualizing the result.

### Initial Analysis

Let's start by loading both files and inspecting their contents:

```python
import torch

base_model = torch.load("base_model.pt", map_location="cpu", weights_only=True)
adapter = torch.load("lora_adapter.pt", map_location="cpu", weights_only=True)

print("Base model keys:", list(base_model.keys()))
print("Adapter keys:  ", list(adapter.keys()))
```

Output:

```
Base model keys: ['layer1.weight', 'layer1.bias', 'layer2.weight', 'layer2.bias',
                'layer3.weight', 'layer3.bias', 'output.weight', 'output.bias']
Adapter keys:   ['layer2.lora_A', 'layer2.lora_B']
```

We see a 4-layer neural network. The adapter targets **layer2** specifically, with two matrices named `lora_A` and `lora_B`.

### Understanding the Structure

Let's inspect the shapes:

```python
print("layer2.weight shape:", base_model["layer2.weight"].shape)
print("layer2.lora_A shape:", adapter["layer2.lora_A"].shape)
print("layer2.lora_B shape:", adapter["layer2.lora_B"].shape)
```

Output:

```
layer2.weight shape: torch.Size([256, 256])
layer2.lora_A shape: torch.Size([64, 256])
layer2.lora_B shape: torch.Size([256, 64])
```

Key observations:

- `layer2.weight` is a **square 256×256 matrix** — this can represent a grayscale image.
- The adapter stores two low-rank matrices: **B** (256×64) and **A** (64×256) with rank 64.
- The naming convention `lora_A` / `lora_B` is a dead giveaway — this is a **LoRA (Low-Rank Adaptation)** setup.

### Background: What is LoRA?

LoRA modifies neural network weights using a low-rank decomposition. Instead of storing a full updated weight matrix, it stores two smaller matrices **A** and **B** such that the update is:

```
W_merged = W + B @ A
```

Where `@` is matrix multiplication. This means the adapter encodes a structured perturbation to the original weights.

### Applying the LoRA Merge

Following the LoRA formula:

```python
W = base_model["layer2.weight"]
lora_A = adapter["layer2.lora_A"]
lora_B = adapter["layer2.lora_B"]

W_merged = W + lora_B @ lora_A
```

Let's check if the merged values fall into a meaningful range:

```python
print(f"Merged range: [{W_merged.min():.4f}, {W_merged.max():.4f}]")
```

Output:

```
Merged range: [0.0000, 1.0000]
```

The values fall neatly into [0, 1] — exactly the range of a normalized grayscale image. This is suspicious and intentional.

### Visualization

A 256×256 matrix with values in [0, 1] is essentially a grayscale image. Let's visualize it:

```python
import matplotlib.pyplot as plt

W_np = W_merged.numpy()
W_min, W_max = W_np.min(), W_np.max()
W_norm = (W_np - W_min) / (W_max - W_min)

plt.figure(figsize=(6, 6))
plt.imshow(W_norm, cmap="gray", interpolation="nearest")
plt.title("Merged Weight Matrix")
plt.axis("off")
plt.savefig("flag.png", dpi=150, bbox_inches="tight")
plt.show()
```

### Flag Retrieval

The resulting image clearly shows the flag text rendered in the weight matrix:

```
apoorvctf{l0r4_m3rg3}
```

### Complete Solve Script

```python
import torch
import numpy as np
import matplotlib.pyplot as plt

# Load files
base_model = torch.load("base_model.pt", map_location="cpu", weights_only=True)
adapter = torch.load("lora_adapter.pt", map_location="cpu", weights_only=True)

# Identify target layer from adapter keys
target_layer = list(adapter.keys())[0].rsplit(".lora_", 1)[0]
weight_key = f"{target_layer}.weight"

# Merge LoRA
W = base_model[weight_key]
lora_A = adapter[f"{target_layer}.lora_A"]
lora_B = adapter[f"{target_layer}.lora_B"]
W_merged = W + lora_B @ lora_A

# Normalize and visualize
W_np = W_merged.numpy()
W_norm = (W_np - W_np.min()) / (W_np.max() - W_np.min())

plt.figure(figsize=(6, 6))
plt.imshow(W_norm, cmap="gray", interpolation="nearest")
plt.axis("off")
plt.savefig("flag.png", dpi=150, bbox_inches="tight")
plt.show()
```

### Conclusion

This challenge tests knowledge of LoRA adapters and neural network weight inspection. The key insights are:

1. Recognizing `lora_A` / `lora_B` as LoRA matrices and understanding the merge formula `W_new = W + B @ A`.
2. Noticing the 256×256 square weight matrix can be interpreted as an image.
3. Applying the merge and normalizing the result to reveal the flag rendered as text in the weight matrix.

No inference, training, or deep ML expertise was needed, just model inspection and basic tensor manipulation.
