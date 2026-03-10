
>Engraver's Fault

>Flag: apoorvctf{1d3nt1ty_cr1515_f0r_1m4g35_h4h4h4}

Description:

In the sun-drenched workshops of Alexandria, it was whispered that no two gemstones are truly pure. When a master carver shaped a signet from carnelian or jasper, the bronze drill left behind a mechanical biography—invisible fissures and unique patterns of grit that no two stones shared. When this seal is pressed into hot wax, it transfers a topography of error. Even if two rings depict the same image, the physical "static" of the stone remains an immutable witness. To the merchant, it is a seal. To the light, it is a map of permanent, invisible scars. We have gained access to a hidden gallery of impressions—a private collection of wax tablets and plaster casts recovered from the conspirators’ inner sanctum. To the untrained eye, it is merely an exquisite art gallery of familiar places: trees,plants,buildings if you look closely, maybe, they had very advanced way of sending messages,a covert communication channel.

Files given:
Chal1.zip(containing gallery folder)
Link: https://drive.google.com/drive/folders/14nPrKeUiYG0wqs1bvsLrS2sHxKj8DYs8?usp=sharing


Author:nnnnn


>**Background;TLDR;**(Skip to solution if you do not want to know about the background)

When I was creating this challenge, I initially thought of finding a way to make people know about an incredible technique actual criminal forensics people use..

So the story is about workshops in ancient Alexandria. Where Artisans and gem cutters used bronze drills to carve designs onto stones

<img src="Attachments/Pasted image 20260309110545.png" width="318">

now, further, it mentions, that however precise the cutters try, they could not ever make two identical designs, there would always be a mark of a stone due to some imperfections.....

Now back to the present, 
Modern day cameras are Made out of CMOS sensors(Complementary Metal-oxide Semiconductors), Hence they require precise lithography based fabrication...So in short, Camera basically has 3 parts:

- Image sensor
- Lens System
- Image signal processor
The important part for our discussion is Image sensor
It kinda looks like this :

<img src="Attachments/Pasted image 20260309111501.png" width="290">

So basically, what happens, Lights(photon) strike onto the photodiode, whose energy then knocks out electron (creates electron hole pair), hence,now more are the photons, more electrons accumulate, this causes the proportional reading of brightness, Hence, Pixel electronics measure the accumulated electrons, The charge is converted to voltage, and then ADC(analog to digital converter) converts this to digital number(which we call pixel brightness)

Not every photon produce a electron hole pair, this is called QE factor(Fancy of Quantum efficiency).
This, specific factor depend on the sensor design. Now, However hard the lithography machine try, like, however precise they are, there are always, photo-diode area differences, doping concentration differences, which gives EVERY sensor its own Fingerprint sort of

THISSSSS is called PRNU(Photo Response Non Uniformity)

There is a way to quantify PRNU's, Lots of research has already been done, 

The most basic use of this , is to make a fingerprint of a Camera's sensor, As these fingerprints are Physically Unclonable Functions(fancy term for no two senors having same fingerprint), We can almost certainly Identify if a particular Image belongs to that camera or not.

This has been in practical use in Criminal Digital Forensics for a while now, Famous case include 
State Vs Thomas D. Pratt , where, 
Pratt claimed that the photos of child exploitation found in his possession were not taken by him, Instead were downloaded from the internet, But, when his camera was seized, and this Exact technique was applied( demonstrated by  Dr. Jessica Fridrich) on it, It was found, The photos indeed emerged from his Own camera!!!!!


Back to the discussion, For calculating PRNU of a camera, you need reference images, ,of, camera, like a lot of them, 100 is generally considered fine

What you do is, 

See, every image contain 

Image= Ideal image(smoothened out) + fingerprint noise + random noise

what you do to find fingerprint 

you take 100 of images each having all these 3 parts

you apply denoising filter(which are accurate to an extent), which leaves the image to be 
ImageNew= Ideal image(smoothened out)

now you subtract ImageNew from Image
giving

Image-ImageNew= Fingerprint Noise + Random noise

here is the use of 100 images

when you do this for all images, and mean them up , the random noise gets cancelled(thats why we need different images, not same ones)

hence, final image left, is almost a pure fingerprint noise, which should be constant for all images!!!, This way ,you found out, the fingerprint!!Some implementation based fine tuning is applied, but not necessary for discussion 

Now , when you correlate PCE factor(correlation factor, as mentioned in resarch paper) of image to be identified, with this fingerprint,if you get PCE > 50 , its a match, if not, Its not a match

references:
Read:
- https://www.researchgate.net/publication/3455253_Digital_Camera_Identification_From_Sensor_Pattern_Noise

- https://ws2.binghamton.edu/fridrich/Research/EI7254-18.pdf




Solution
-------------------------------------------------------

>**Initial thought:**

Once you read the Description, and see the files inside gallery folder, you get , some files named starting from "IMG_" and some are numbered 1,2,3,4

You then try all general Image steg tools, binwalk, zsteg, file, foremost, aperisolve , and all, you get nothing

One thought that should immediately some to mind is IMG_ is taken from a camera/or a hardware that serially orders images in a specific format, Camera in this case. Now based on the challenge description, It is calling out to say, that, one could, say, a permanent mark/fingerprint of certain hardware. In this case camera, Once , we search online,We immediately get PRNU, and further studies on it

You read about it and all
<img src="Attachments/Pasted image 20260309115937.png">

>Process


Now, when we think, how could flag message be. The only click that you need to solve this challenge now, is the thought that images are ordered sequentially, 

now, as you already now know PRNU, Images, you get that, its standard PRNU identification of ordered images, 

and all the images starting from IMG_ are the reference images, taken from same camera

all you have to do now is 

- create a new folder for all IMG_ images
- Calculate Fingerprint using those
- Sequentially check each numbered image, If its a match, use 1 , else use 0, you will get the binary sequence, which converted to text gives you the flag

There are different implementations of PCE based PRNU available 

one is PRNU-python (polimi-ispl)
another project you would find on github is ShutterTrace(which is go based implementation of prnu extraction)

	I have used ShutterTrace for this writeup


First I separate IMG_ from numbered images 

`mkdir img_files numbered_files`
`mv IMG_* img_files/`
`mv [0-9]*.jpg numbered_files/`

Now, We create a fingerprint using the img_files, go to ShutterTrace folder, run

```
./ShutterTrace enroll \
--camera chal_cam \
--in ~/Desktop/chal1/gallery/img_files \
--out ./db \
--sigma 1.0
```
in --in, use your folder path to img_files
it will now take some time to process all, i guess 103 images 

<img src="Attachments/Pasted image 20260309122612.png">

<img src="Attachments/Pasted image 20260309122733.png">


Now that we have the fingerprint, 

lets verify 1st image in numbered_files, using inbuild Shuttertrace identification 


 ```
 ./ShutterTrace verify \
--camera chal_cam \
--db ./db \
--img ~/Desktop/chal1/gallery/numbered_files/1.jpg \
--metric both
 ```

<img src="Attachments/Pasted image 20260309124231.png">
Its PCE is negative, so no match , first bit is 0

lets verify 2nd image in numbered_files, using inbuild Shuttertrace identification 


 ```
 ./ShutterTrace verify \
--camera chal_cam \
--db ./db \
--img ~/Desktop/chal1/gallery/numbered_files/2.jpg \
--metric both
 ```

<img src="Attachments/Pasted image 20260309124042.png">
PCE is greater than 40/50 ,matches, second bit is 1


you can do this for all images in numbered_files folder, using automated script  , you will finally get the binary sequence:

>0110000101110000011011110110111101110010011101100110001101110100011001100111101100110001011001000011001101101110011101000011000101110100011110010101111101100011011100100011000100110101001100010011010101011111011001100011000001110010010111110011000101101101001101000110011100110011001101010101111101101000001101000110100000110100011010000011010001111101


When converted to text gives the flag 


>apoorvctf{1d3nt1ty_cr1515_f0r_1m4g35_h4h4h4}



To Optimize this further, ShutterTrace calculates some unnecessary things too, we calculate PCE from the research paper way itself, and use prnu-library from prnu-python(polimi-ispl) to calculate noise of each subject image using extract_single function 

here is the multi-core-optimized script



```
import os
import glob
import numpy as np
from skimage import io
from scipy.fft import fft2, ifft2
from multiprocessing import Pool, cpu_count
from prnu import extract_single

# -----------------------
# CONFIG
# -----------------------

FINGERPRINT_PATH = "ShutterTrace/db/chal_cam/fingerprint.bin"
IMAGE_FOLDER = "/home/fivetimesfourteen/Desktop/chal1/gallery/numbered_files"
PCE_THRESHOLD = 60
MAX_IMAGES = None   # Set to number if you want limit

# -----------------------
# Load fingerprint
# -----------------------

K = np.fromfile(FINGERPRINT_PATH, dtype=np.float32)
K = K.reshape((3072, 4096))
K_fft = fft2(K)

print("Fingerprint loaded:", K.shape)

# -----------------------
# PCE computation
# -----------------------

def compute_pce(W):
    C = np.real(ifft2(fft2(W) * np.conj(K_fft)))

    peak = np.max(C)
    peak_idx = np.unravel_index(np.argmax(C), C.shape)

    mask = np.ones_like(C, dtype=bool)
    r, c = peak_idx

    r0 = max(r - 5, 0)
    r1 = min(r + 6, C.shape[0])
    c0 = max(c - 5, 0)
    c1 = min(c + 6, C.shape[1])

    mask[r0:r1, c0:c1] = False
    background = C[mask]

    energy = np.mean(background ** 2)
    pce = (peak ** 2) / energy

    return pce

# -----------------------
# Worker
# -----------------------

def process_image(path):
    img = io.imread(path)
    W = extract_single(img)
    pce = compute_pce(W)

    verdict = "SAME" if pce > PCE_THRESHOLD else "DIFFERENT"
    bit = "1" if verdict == "SAME" else "0"

    return (os.path.basename(path), pce, verdict, bit)

# -----------------------
# Main
# -----------------------

if __name__ == "__main__":

    # Strict numeric sort (1.jpg, 2.jpg, 3.jpg...)
    images = sorted(
        glob.glob(os.path.join(IMAGE_FOLDER, "*.jpg*")),
        key=lambda x: int(os.path.splitext(os.path.basename(x))[0])
    )

    if MAX_IMAGES:
        images = images[:MAX_IMAGES]

    print("Images found:", len(images))
    cores = cpu_count()
    print("Using CPU cores:", cores)
    print()

    reconstructed_binary = ""
    same = 0
    different = 0

    # Use imap (ordered)
    with Pool(cores) as pool:
        for name, pce, verdict, bit in pool.imap(process_image, images):

            if verdict == "SAME":
                same += 1
            else:
                different += 1

            reconstructed_binary += bit

            print(f"{name:10} | PCE={pce:.2f} | {verdict}")

    print("\nSummary:")
    print("Same camera:", same)
    print("Different camera:", different)

    print("\nReconstructed Binary:")
    print(reconstructed_binary)

```
























































































































