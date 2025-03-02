## Split Lies
In the age of the samurai, a forbidden scroll was split into two layers to conceal its secret. Only a warrior with keen vision can reunite them and reveal the truth. 

- Author: Laav10
- flag: apoorvctf{L4y3R3d_T2u7H}
- Category: Cryptography / Misc


## Writeup

This challenge is based on Visual Cryptography, where an image is split into multiple layers that appear as random noise but reveal information when combined. Our goal is to reconstruct the hidden message from the provided layers.

After downloading the given images (part1.png and part2.png), we notice that they appear as seemingly random CMYK patterns. This is a common characteristic of (2,2) visual cryptography schemes, where each layer alone is meaningless.

To reconstruct the original message, we need to overlay both images. This can be done manually or using Python(PIL/OpenCV).

Once the images are combined, the flag is embedded in a moire pattern. Zoom in carefully to observe the text.