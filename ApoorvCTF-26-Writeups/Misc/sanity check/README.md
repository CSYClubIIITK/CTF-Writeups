>Sanity check

>Flag:apoorvctf{d0n7_w0rry_y0u_4r3_s4n3}

Description:
Hallo, Wave 2 has been released , Happy pwning

Hints(21 points)

Solution:

This question was released in the wave 2
If you look at the description again, You would notice there is a misspell, "Hallo" instead of hello

as announced by makeki many times, everything you need is in discord, 
if you read the announcements of wave 2 again, it has the same misspell Hallo , instead of hello, pointing you that sanity check is related to this announcement,anyways Hint clearly states to read into announcements again

when you copy the text, and put in cyberchef or any other similar tool, you get 
<img src="Attachments/Pasted image 20260309134534.png">
 There it is , there are some hidden characters in it, classic invisible unicode steg...

convert the message to hex, to get which characters are used

<img src="Attachments/Pasted image 20260309134831.png">


Unicode characters identified:
`e2 80 8c`-U+200C
`e2 80 8d` -U+200D
`e2 80 aa`-U+202A
`e2 80 ac`- U+202C
`ef bb bf`- U+FEFF

go to any online decoder, popular one is :https://330k.github.io/misc_tools/unicode_steganography.html

use options:

<img src="Attachments/Pasted image 20260309135101.png">

Put the copied announcement into steganography text section, click decode

there you go, you get the flag
<img src="Attachments/Pasted image 20260309135211.png" width="528">


>apoorvctf{d0n7_w0rry_y0u_4r3_s4n3}

