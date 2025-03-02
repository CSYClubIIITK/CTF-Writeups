## Description
A criminal mastermind named larry stole Chef Tataka ultimate ramen recipe and yeeted it into a password-protected zip file. Inside? A sacred text file with the secret to flavor nirvana. Crack the zip, save the slurp. No pressure. 🍜💀

- Author: hampter
- flag: apoorvctf{w0rst_r4m3n_3v3r_ong}
- files: recipe.zip
- Category: Forensics

## Writeup
Here we have a zip file, when we try to unzip it `unzip recipe.zip` it asks for a password.

So we either need to find the password or bypass it somehow.

First thing i ran `unzip -l recipe.zip` 
```
Archive:  recipe.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    89796  2025-02-24 18:37   secret_recipe.png
---------                     -------
    89796                     1 file
```
So the zip only contains one png file named `secret_recipe.png`

Next thing i started researching about some kind of vulnerability in protected zip files. 

I found an article mentioning about some known plainext attack in **PKZIP stream cipher**
[https://link.springer.com/chapter/10.1007/978-3-642-31912-9_16](https://link.springer.com/chapter/10.1007/978-3-642-31912-9_16)

Found a tool to exploit this vulnerability on github called [bkcrack](https://github.com/kimci86/bkcrack)

But in order for this attack to work we need to know some plaintext that exists in our zip file.

Now we know the file inside is a PNG and what plaintext is present in all PNG's - `The magic string`

We know every png starts with `89 50 4E 47 0D 0A 1A 0A` but this attack requires at least 13 bytes to be effective so i also added the IHDR chunk as all PNG's must have a ihdr chunk hence we know `89 50 4E 47 0D 0A 1A 0A 00 00 00 0D 49 48 44 52` exists in our file.

So our plaintext is 
```
�PNG

IHDR
```
save this as `png.bin`

run `bkcrack -C recipe.zip -c secret_recipe.png -p png.bin`

- recipe.zip is the zip file
- secret_recipe.png is the cipher text(Since we know plaintext from png)
- png.bin is the magic string of PNG with IHDR

After running this we get
```
bkcrack 1.7.1 - 2024-12-21
[18:43:49] Z reduction using 9 bytes of known plaintext
100.0 % (9 / 9)
[18:43:49] Attack on 721680 Z values at index 6
Keys: 7cfefd6a 4aedd214 970c7187
41.3 % (297837 / 721680)
Found a solution. Stopping.
You may resume the attack with the option: --continue-attack 297837
[18:47:12] Keys
7cfefd6a 4aedd214 970c7187
```

Hurray! We got the internal keys `7cfefd6a 4aedd214 970c7187`

Now we use `bkcrack -C recipe.zip -k 7cfefd6a 4aedd214 970c7187 -D unprotected.zip` (this will make a clone of original zip without password)

Now unzip the new zip `unzip unprotected.zip`
Open secret_recipe.png in any image viewer to get the flag.
