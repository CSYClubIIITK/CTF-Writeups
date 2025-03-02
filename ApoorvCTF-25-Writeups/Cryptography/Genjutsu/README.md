## Genjutsu Labyrinth
Genjutsu Labyrinth is filled with hidden secrets and illusions. We’ve uncovered some clues about the escape, but reality isn’t always what it seems. Can you see through the deception and find the way out?

- Remarks: Attach broken.py along with the description. Genjutsu.py will be running on the instance. 
- Author: Laav10
- flag: apoorvctf{G3NJUTSU_M4ST3R}
- Category: Cryptography - Instance Based


## Writeup

The challenge is a  grid-based problem where the escape depends on analyzing the values of a and b. The key observations are:

    b = 0, which means it has no effect on calculations.
    a takes prime values less than 12, i.e., {2, 3, 5, 7, 11}.
    The grid simplifies to values of the form a * n.

This transformation allows us to represent the grid purely in terms of multiplication without additional complexity.
The challenge is now simplified to finding minimal XOR path. 