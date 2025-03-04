# Kenzo's Whispers

## Description
In the shadow of Eisler Memorial Hospital, where the echoes of one fateful decision still linger in its sterile corridors, a series of enigmatic audio files has surfaced. Layered with multiple voices, these recordings conceal hidden signals—subtle messages buried deep within a dense forest of sound, shrouded in a veil of secrecy like moss creeping over forgotten truths.

Dr. Kenzo Tenma’s legacy is one of choices that shape fate. His fateful decision unraveled a web of conspiracies and secrets that defied the natural order. Now, the mystery resurfaces, beckoning you to follow in his footsteps. Your challenge is to decode this collection of cryptic audio landscapes and uncover the truth—before Johan Liebert gets there first.

Download challenge files: https://drive.google.com/file/d/1FNRR6CqrRdSpQioHmoIHDVeVdUMxO6Jr/view?usp=sharing

- Author: J Glen Enosh
- flag: apoorvctf{B3at_$ynTh_4I_9000}

## Misc
The eval will be done using a netcat server.
## Writeup

## Overview
This guide walks you through solving the Morse Code Challenge. Follow these steps to extract the hidden flag.

---

## Steps to Solve

### 1️⃣ Identify Morse-coded Files Using Random Forest
- Train a **Random Forest classifier** to distinguish Morse-coded files.
- Extract features and classify.
- Identify the **8 files** containing Morse-coded information.
- **[INSERT IMAGE: Random Forest classification process]**

### 2️⃣ Alternative Approach: Using File Listing
- Navigate to the `clips` folder.
- Run the command:
  ```bash
  ls -lat | head -n 20
  ```
- Observe that 8 files were recently added on **March 1st**, while others are from **December 8th**.
- These 8 files contain Morse-coded information.
- ![alt text](<Screenshot from 2025-03-04 12-45-37.png>)

### 3️⃣ Decode Morse Code
- Convert Morse-coded audio to text.
- Extract **8 ordered phrases**.

### 4️⃣ Submit Phrases for Password
- Submit the extracted phrases to the **eval system**.
- Receive a **password**.

### 5️⃣ Extract Hidden JSFuck from README
- Locate **line 700** of the `README` file.
- Identify hidden **JSFuck** code.

### 6️⃣ Decode JSFuck to Get Google Drive Link
- Use a **JSFuck decoder**.
- Extract a **Google Drive link**.

### 7️⃣ Download & Unlock ZIP
- Download the **ZIP file** from the link.
- Unlock using the **password**.
- Extract its contents.

### 8️⃣ Convert Binary Data into an Image
- Identify the **binary data**.
- Convert it to an **image**.
- **[INSERT IMAGE: Binary to image conversion]**

### 9️⃣ Scan Spotify Code
- The image contains a **Spotify Code**.
- Scan it using the **Spotify app**.
- ![alt text](Sportify.png)

### 🔟 Extract Flag from Playlist Cover
- The Spotify playlist **cover image** contains the **flag**.
- ![alt text](<Screenshot from 2025-03-02 08-27-30.png>)
---

## 🎯 Conclusion
By following these steps, you successfully retrieve the hidden flag. Well done!

---

**Happy Hacking!** 🚀



 ## Files to be shared :
    1 zip folder containing the following files/folders :
    - clips
    - Readme.txt
