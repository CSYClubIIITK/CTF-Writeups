#  Prerequisites
```bash
pip install numpy pillow
```
---
# Description
- The challenge requires to find the determinants for the matrices that are used as kernels in feature extraction during the Image processing in Convolution Neural Networks.
- The determinants are then appended to each other using `_` underscores to retrieve as flags.
E.g.:
- If the determinants are 2, 24, 17, then the flag is apoorvctf{2_24_17}
- First, pass the image names as arguments to the `retrieve_kernel.py`.
```bash
python retrieve_kernel.py flower.jpg flower_processed.jpg
```
- This prints three matrices corresponding to each of the RGB layer.
- Find the determinant of the matrices and pass it to `process_scalars.py` in the same RGB order.
```bash
python process_scalars.py 12 40 35
```
- This outputs the flag as `apoorvctf{12_40_35}`