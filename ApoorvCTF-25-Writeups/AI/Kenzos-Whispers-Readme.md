# Kenzo's Whispers

### Description
In the shadow of Eisler Memorial Hospital, where the echoes of one fateful decision still linger in its sterile corridors, a series of enigmatic audio files has surfaced. Layered with multiple voices, these recordings conceal hidden signals—subtle messages buried deep within a dense forest of sound, shrouded in a veil of secrecy like moss creeping over forgotten truths.

Dr. Kenzo Tenma’s legacy is one of choices that shape fate. His fateful decision unraveled a web of conspiracies and secrets that defied the natural order. Now, the mystery resurfaces, beckoning you to follow in his footsteps. Your challenge is to decode this collection of cryptic audio landscapes and uncover the truth—before Johan Liebert gets there first.

Download challenge files: https://drive.google.com/file/d/1FNRR6CqrRdSpQioHmoIHDVeVdUMxO6Jr/view?usp=sharing

- Author: J Glen Enosh
- flag: apoorvctf{B3at_$ynTh_4I_9000}

### Misc
The eval will be done using a netcat server.
### Writeup
We have a collection of audio files (int the clips folder), among which 8 contain Morse-coded information. Follow the steps to get the answer:
Identify Morse-coded files using Random Forest classification.
Decode Morse code to get 8 ordered phrases.
Submit phrases to eval to obtain a password.
Extract and decode hidden JSFuck from line 700 of README.
Decode JSFuck to get a Google Drive link.
Download & unlock ZIP with the password.
Convert binary data into an image.
Scan the image’s Spotify Code.
Extract the flag from the playlist cover image.

 ### Files to be shared :
    1 zip folder containing the following files/folders :
    - clips
    - Readme.txt
