## I Love Japan: Flag Hunt
My friend who sent the pretty.jpeg challenged you to find a flag for this one!
He thinks he codes well, bruh! he has commitment issues.

- Author: Laav10
- flag: apoorvctf{Fr13ndsh1p_G04ls}
- Category: OSINT


## Writeup

The challenge is connected. A simple strings on pretty.jpeg from the previous challenge gives us his username: Shinkirokaze

A Github search for the username will lead to the account and the Repository Esoteric.
The flag is encrypted in AES 256 and is displayed in the commits made. It can be decrypted with the key apoorvctf{f4k3d}.


