# Phantom Connection

## Description
Like a fleeting dream, a connection once existed but has faded into the void. Only shadows of its presence remain. Can you bring it back to light?

- Author: Suraj
- flag: apoorvctf{CAcH3_Wh4T_YoU_sE3}

**Category : Forensics**

## Writeup
## Challenge Description

We've given a mysterious cache folder containing files like `Cache0000.bin` and `bcache24.bmc`. Our task is to identify what these files are, extract their contents, and reconstruct the information to reveal a hidden flag.


### File Identification

When first encountering these files, standard tools provide limited information:

```bash
$ file Cache0000.bin 
Cache0000.bin: data

$ file bcache24.bmc 
bcache24.bmc: empty
```

This requires deeper research. A good approach is to:
1. Search for file extensions online (`.bmc` and `.bin`)
2. Look for patterns in the file names and structure

Through research, you'll discover these files are related to Microsoft's Remote Desktop Protocol (RDP) bitmap caching system, which stores screen fragments from remote desktop sessions.

### Extracting Bitmap Data with BMC-Tools

After identifying these as RDP cache files, you'll need to extract the bitmap data. The primary tool for this is BMC-Tools:

```bash
$ git clone https://github.com/ANSSI-FR/bmc-tools.git
$ cd bmc-tools
```

Use the tool to extract bitmap images from the cache files:

```bash
$ python bmc-tools.py -s /path/to/bin_file -d output_directory
```

The script will process the cache files and extract all bitmap images:

```
[+++] Processing a single file: 'Cache0000.bin'.
[+++] Processing a file: 'Cache0000.bin'.
[===] 1980 tiles successfully extracted in the end.
[===] Successfully exported 1980 files.
```

This will give you a collection of bitmap fragments extracted from the cache files.

### Understanding RDP Bitmap Caching

Now that you've extracted the bitmaps, it's helpful to understand what you're looking at:

- RDP uses a bitmap caching mechanism to improve performance
- It stores frequently used screen elements to reduce bandwidth
- The cache contains fragments of what was displayed during remote sessions
- These fragments need to be pieced together to reconstruct the complete screens

### Reconstructing the Flag

After extraction, you'll have multiple bitmap fragments in the output_directory. There are two approaches to finding the flag:

#### Manual Reconstruction:
1. Examine all extracted images carefully
2. Look for fragments containing parts of text that might be the flag
3. Arrange the fragments in a logical order

You may find parts of the flag spread across multiple bitmap fragments. By arranging them correctly, you can read the complete flag.

#### Using RDPCacheStitcher:
For more complex reconstruction, we can use RDPCacheStitcher, a tool specifically designed to help organize and visualize RDP cache fragments
You can create a new case with the folder containing the bmp files and manually drag and drop them to the window like solving a puzzle

After reconstructing you can see the flag as

**Flag:`apoorvctf{CAcH3_Wh4T_YoU_sE3}`**
