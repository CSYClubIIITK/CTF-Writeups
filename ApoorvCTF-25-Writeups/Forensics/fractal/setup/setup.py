import numpy as np
from PIL import Image

def generate_fractal(size=1024, max_iter=100):
    fractal = np.zeros((size, size), dtype=np.uint8)
    
    for x in range(size):
        for y in range(size):
            real = (x / size) * 3.5 - 2.5
            imag = (y / size) * 2.0 - 1.0
            c = complex(real, imag)
            z = complex(0, 0)
            iter_count = 0
            
            while abs(z) < 2 and iter_count < max_iter:
                z = z*z + c
                iter_count += 1
            
            fractal[x, y] = int((iter_count / max_iter) * 255)
    
    return fractal

def save_fractal(fractal, filename="fractal.png"):
    image = Image.fromarray(fractal.astype(np.uint8))
    image.save(filename)

def embed_flag(fractal, flag):
    fractal = fractal.astype(np.uint8)  
    binary_flag = ''.join(format(ord(c), '08b') for c in flag)  
    binary_flag += '00000000'  

    indices = np.argwhere(fractal > 128)  
    indices = sorted(indices, key=lambda x: (x[0], x[1]))  

    if len(binary_flag) > len(indices):
        raise ValueError("Not enough space in fractal to embed flag!")

    for i, bit in enumerate(binary_flag):
        x, y = indices[i]
        fractal[x, y] = (fractal[x, y] & ~1) | int(bit)
    
    return fractal


def extract_flag(image_path="fractal.png"):
    image = Image.open(image_path).convert('L')
    fractal = np.array(image)
  
    indices = np.argwhere(fractal > 128)
    indices = sorted(indices, key=lambda x: (x[0], x[1]))
    
    binary_flag = ''.join(str(fractal[x, y] & 1) for x, y in indices)

    flag = ''.join(chr(int(binary_flag[i:i+8], 2)) for i in range(0, len(binary_flag), 8))

    flag = flag.split('\x00', 1)[0]
    
    return flag


fractal = generate_fractal()
try:
    with open("flag.txt", "r") as flag_file:
        flag = flag_file.read().strip()
except:
    flag = "apoorvctf{fake_flag}"

fractal_with_flag = embed_flag(fractal,flag)
save_fractal(fractal_with_flag)

decoded_flag = extract_flag()
print(f"Extracted Flag: {decoded_flag}")

