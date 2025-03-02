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
    # Code
    return fractal

def get_flag():
    try:
        with open("flag.txt", "r") as flag_file:
            flag = flag_file.read().strip()
    except:
        flag = "apoorvctf{fake_flag}"
    return flag

if __name__ == "__main__":
    fractal = generate_fractal()
    flag = get_flag()
    fractal_with_flag = embed_flag(fractal,flag)
    save_fractal(fractal_with_flag)

