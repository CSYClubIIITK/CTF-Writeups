## Description
Unveil the lost code of the Samurai and unlock the mystery hidden within.

- Author: Suraj
- flag: apoorvctf{ByT3s_OUT_OF_ORd3R}

**Category : Forensics**


## Writeup
An image file is provided, and analyzing it with the `strings` command reveals some unusual text at the end. This piece of tect is Brainfuck code.

Decoding the Brainfuck script using an online interpreter reveals a Google Drive link. Accessing the link leads to a single file named *samurai*, with no extension or other identifying details.

To determine the nature of the file, the `file` command is executed:

```bash
file samurai
```

The output simply states *data*, meaning the file type is not recognized.  Opening the file in a hex editor like `ghex` reveals the first few bytes as `D8 FF E0 FF`.

This closely resembles the standard JPEG header (`FF D8 FF E0`), except that each consecutive byte pair appears to be swapped.

Recognizing this byte-swapping pattern suggests that the original file structure can be restored by reversing the swaps. We can write a python script to swap every consecutive byte pair back into the correct order:

```python
def reverse_swap_concurrent_bytes(input_file, output_file):
    with open(input_file, "rb") as f:
        data = bytearray(f.read())

    for i in range(0, len(data) - 1, 2):
        data[i], data[i + 1] = data[i + 1], data[i]

    with open(output_file, "wb") as f:
        f.write(data)

reverse_swap_concurrent_bytes("samurai", "restored.jpg")
```

Executing the script:

```bash
python3 restore.py
```

This gives a new file, *restored.jpg*. Opening the file we can see the flag. 



**Flag: `apoorvctf{ByT3s_OUT_OF_ORd3R}`**
