
>Beneath The armor

>Flag: apoorvctf{m0dul4r_4r17hm371c_15_fun_y34h}

Description:History repeats itself, even for ironman, life goes on cycles

Files:challenge.png
Link: https://drive.google.com/drive/folders/1j5WNuxIk0C30_wE30aM_JiALF3n3lLoV?usp=sharing



Solution:

first we perform all common tools on png, zsetg, file, binwalk, exiftool, aperisolve, lsb extraction, foremost 
we get nothing, 

Ironman-hmm, smart, genius, playboy, billionare
makes things by himself, maths and science, tech!!!!!!!



now looking at the challenge description again, and pondering, There has to be something related to cycles, 
The Title clearly suggests something is hidden, inside bytes, 
The most common LSB and MSB fail
once these parts are linked

LSB/MSB and cycles, repetition, maths

cycles,repetition,maths
cycles,repetition,maths
cycles,repetition,maths

use 0 mapped to R, 1 Mapped to G, 2 mapped to B


>if we do integer mod1 cycle
0mod1=0-> (R0)
1mod1=0->  (R0)
2mod1=0-> (R0)
.....
so the extraction become, R0R0R0R0R0R0R0R0R0.....



>if we do integer mod2 cycle
0mod2=0->(R0)
1mod2=1->(G1)
2mod2=0->(R0)
3mod2=1->(G1)

extraction becomes . R0G1R0G1R0G1R0G1

>if we do integer mod 3 cycle
0mod3=0->(R0)
1mod3=1->(G1)
2mod3=2->(B2)
3mod3=0->(R0)
4mod3=1->(G1)
5mod3=2->(B2)

if we do integer mod4 cycle, there should be atleast 4 colors in image, so, we do not do that 

in the third iteration itself, we get the flag 


here is the script:

```
from PIL import Image

img = Image.open("challenge.png").convert("RGB")
pixels = list(img.getdata())

raw = []
for r, g, b in pixels:
    raw.extend([r, g, b])

cycle = int(input("Enter cycle number: "))

bits = []
for i, val in enumerate(raw):
    bit = (val >> (i % cycle)) & 1
    bits.append(bit)

out = bytearray()
for i in range(0, (len(bits)//8)*8, 8):
    byte = 0
    for b in bits[i:i+8]:
        byte = (byte << 1) | b
    out.append(byte)

print(out.decode("utf-8", errors="ignore")[:200])
```

