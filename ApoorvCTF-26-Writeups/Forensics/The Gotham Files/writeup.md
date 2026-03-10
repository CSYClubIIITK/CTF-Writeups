# TheGothamFiles

## Description

A mysterious panel surfaced at this year's ComiCon. The artist left something behind.

- **Author:** n3twraith
- **Category:** Forensics
- **Difficulty:** Medium

---

# Writeup

## Challenge Overview

The challenge provides a single file:

```
challenge.png
```

At first glance, the image appears to be a normal Batman comic panel. However, the challenge description hints that something hidden is embedded within the image.

The first step is to inspect the metadata.

---

# Initial Analysis

We begin by examining the file metadata using `exiftool`.

```bash
exiftool challenge.png
```

Output:

```
Artist  : The Collector
Comment : Not all colors make it to the page. In Gotham, only the red light tells the truth.
```

Two important hints appear:

1. **"Not all colors make it to the page"**
2. **"Only the red light tells the truth"**

These hints strongly suggest that the hidden data relates to **color channels** and possibly **unused colors**.

Next, we inspect the file type.

```bash
file challenge.png
```

Output:

```
challenge.png: PNG image data, 1920 x 1200, 8-bit colormap
```

The key observation here is:

```
8-bit colormap
```

This indicates the image is an **indexed PNG** rather than a standard RGB PNG.

---

# PNG Palette Analysis

To confirm this, we inspect additional information about the palette.

```bash
identify -verbose challenge.png | grep -i "color\|type\|palette"
```

Output:

```
Type: Palette
Colors: 200
Colormap entries: 256
```

This reveals something interesting.

The image palette contains **256 entries**, but the image only uses **200 colors**.

Therefore:

```
256 - 200 = 56 unused palette entries
```

These unused palette entries exist inside the PNG file but **are never referenced by any pixel in the image**.

This makes them an ideal place to hide data.

---

# Indexed PNG Structure

Unlike RGB images where each pixel stores `(R,G,B)` values, indexed PNG images store palette indices.

A simplified structure looks like this:

```
PLTE chunk → contains palette colors
IDAT chunk → contains compressed pixel indices
```

Example:

```
pixel = 0 → palette[0] → (255,0,0)
pixel = 1 → palette[1] → (0,255,0)
```

If a palette entry is **never referenced**, its RGB values exist inside the file but are never rendered by image viewers.

This aligns with the challenge hint:

> "Not all colors make it to the page"

---

# Exploitation Strategy

From the hints and analysis we infer:

1. The hidden data is stored inside **unused palette entries**.
2. The hint **"only the red light tells the truth"** indicates that the **red channel** contains the hidden bytes.
3. Since CTF flags end with `}`, we can stop extraction once we encounter the ASCII value `0x7D`.

The strategy therefore is:

1. Parse PNG chunks.
2. Extract the **PLTE palette**.
3. Decompress **IDAT pixel data**.
4. Identify which palette indices are actually used.
5. Determine the unused palette entries.
6. Read the **red channel** from those unused entries.
7. Stop once the `}` character is encountered.

---

# Solve Script

```python
import struct
import zlib

def solve(png_file):
    with open(png_file, "rb") as f:
        data = f.read()

    pos = 8
    chunks = []

    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos+4])[0]
        ctype  = data[pos+4:pos+8]
        cdata  = data[pos+8:pos+8+length]

        chunks.append((ctype, cdata))
        pos += length + 12

    ihdr = next(c for t,c in chunks if t == b'IHDR')
    width, height = struct.unpack(">II", ihdr[:8])

    plte = next(c for t,c in chunks if t == b'PLTE')

    palette = []
    for i in range(0, len(plte), 3):
        palette.append((plte[i], plte[i+1], plte[i+2]))

    idat = b''.join(c for t,c in chunks if t == b'IDAT')
    raw  = zlib.decompress(idat)

    used = set()

    for y in range(height):
        row = raw[y*(width+1)+1 : (y+1)*(width+1)]
        used.update(row)

    unused = sorted(set(range(len(palette))) - used)

    flag_bytes = []

    for idx in unused:
        r,g,b = palette[idx]
        flag_bytes.append(r)

        if r == 0x7d:
            break

    flag = bytes(flag_bytes).decode()
    print(flag)

solve("challenge.png")
```

---

# Flag

```
apoorvctf{th3_c0m1cs_l13_1n_th3_PLTE}
```

---
