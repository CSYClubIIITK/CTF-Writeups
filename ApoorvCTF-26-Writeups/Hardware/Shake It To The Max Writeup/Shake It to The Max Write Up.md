#### Question

# **Shake It to the Max**

### Background

The facility wasn’t supposed to exist.

Hidden behind layers of shell companies and abandoned industrial infrastructure, intelligence eventually uncovered a secret research site developing **autonomous UAV swarms** capable of coordinating attacks without centralized control.

These drones were designed to function as a **self-organizing network**. Each unit communicates directly with nearby drones, passing commands from one to another until the entire swarm reacts as a single organism.

No command center.  
No master controller.

Just drones talking to drones.

Every message transmitted inside the swarm passes through a **custom encryption chip** embedded in the communication hardware of each unit. The engineer responsible for the system refused to use commercial components. Instead, he designed the encryptor himself using **simple logic circuits built from discrete components**.

Brilliant.

And deeply unstable.

When your team infiltrated the facility, the swarm’s onboard threat detection system reacted immediately.

Within seconds every drone switched to **destruction mode**.

Rotors screamed to life.  
Weapons armed.  
The swarm began hunting anything it detected.

And then something strange happened.

Across the swarm communication channel, a repeating signal started broadcasting continuously. At first it sounded like interference, but after isolating the transmission it became clear that the drones were actually **playing a song** through their network.

Over and over again, the same track echoes through the swarm:

```
SHAKE IT TO THE MAX
```

According to recovered logs, the engineer programmed the drones to **play this song whenever destruction mode activates**. A signature. A joke. Or maybe something more.

If the swarm communicates entirely through encrypted messages passed from drone to drone, then the phrase repeating across the network might not just be a song.

It might also be a clue.

The shutdown command could be hidden in plain sight.

Unfortunately, any command injected into the swarm must first be transformed exactly the way the **encryptor hardware** would process it.

Among the wreckage of the facility, a few suspicious artifacts were recovered from the destroyed hardware systems. Most storage devices were wiped or physically damaged, but a small number of files survived intact.

These include:

- a **CSV file**
    
- a **circuit diagram**
    

Their purpose is unclear, but they appear to be related to the encryptor hardware used inside the drones.

If the encryptor can be reconstructed, it may be possible to determine what the swarm expects to receive.

The drones are still active.

The song is still playing.

And somewhere inside the system lies the message that can shut them down.

---

### Objective

Determine the **encrypted hexadecimal message** generated when the phrase

```
SHAKEITTOTHEMAX
```

is processed by the drone communication encryptor.

If the correct encoded message is injected into the swarm network, it should propagate between the drones and terminate destruction mode.


> Author:Eappen

# Writeup — _Shake It to the Max_

![[encrypto.png]]

## Overview

The challenge provides a circuit diagram, a CSV file (`encrypto.csv`), and a hint referencing **Quine–McCluskey tables** and the phrase **“min to the max”**.

From the challenge story we already suspect that the phrase:

```
SHAKEITTOTHEMAX
```

is likely the command that needs to be encoded. The main task is therefore to **reconstruct the encryptor logic** and determine the encrypted hexadecimal output produced when this phrase is passed through it.

---

# Understanding the Circuit Diagram

The circuit diagram shows a block labeled **ENCRYPTA** with:

- **8 input pins**
    
- **8 output pins**
    

```
IN0  (MSB)
IN1
IN2
IN3
IN4
IN5
IN6
IN7
```

and outputs

```
OUT0 (MSB)
OUT1
OUT2
OUT3
OUT4
OUT5
OUT6
OUT7
```

The block also contains a control input labeled **MAX**, connected to an **AND gate**.

Two signals feed this AND gate:

- **IN7 (LSB of input)**
    
- **OUT7 (LSB of output)**
    

So the MAX signal becomes active when:

```
IN7 AND OUT7
```

i.e.

```
input LSB = 1
AND
output LSB = 1
```

---

# Behavior of the MAX Signal

The diagram indicates that the **MAX signal affects the encryptor logic itself**.

The provided hint says:

> _"We have found on further inspection some Quine McClusky tables and some min to the max written under the AND logic."_

This hint is crucial.

Quine–McCluskey is an algorithm used for simplifying **Boolean functions expressed in minterms or maxterms**.

From this we infer that:

```
MAX switches the logic between
minterm representation and maxterm representation.
```

In practice, this means:

```
output_bit = function(input)
```

when MAX is off.

But when MAX is on:

```
output_bit = NOT function(input)
```

So MAX simply **inverts the output of every Boolean function**.

This can be implemented with:

```
output = F(input) XOR MAX
```

---

# Interpreting the CSV File

The file `encrypto.csv` contains a table describing the behavior of the encryptor.

Each row corresponds to a possible **8-bit input value**.

Each column corresponds to one of the outputs:

```
OUT0 OUT1 OUT2 OUT3 OUT4 OUT5 OUT6 OUT7
```

By scanning each column we can determine **which input values produce a 1** for that output.

These input values represent the **minterms** of the Boolean function.

For example:

```
OUT0 column
```

If rows

```
3, 5, 9, 14
```

contain `1`, then

```
F0 = Σm(3,5,9,14)
```

This process is repeated for all 8 outputs to build the list:

```
functionList = [F0,F1,F2,F3,F4,F5,F6,F7]
```

where each element contains the list of **minterms for that function**.

---

# MAX Latch Behavior

From the circuit we saw that:

```
MAX = IN7 AND OUT7
```

Meaning MAX becomes active when both the **LSB of the input byte** and the **LSB of the output byte** are 1.

Importantly, the MAX signal affects the **next encryption cycle**, making the encryptor **stateful**.

---

# Implementing the Encryptor

Once the minterm lists are constructed from the CSV file, the encryptor can be reproduced in Python.

The logic works as follows:

1. For each character in the input string
    
2. Convert the ASCII value to an integer
    
3. Compute each output bit using the Boolean functions
    
4. If MAX is active, invert the function outputs
    
5. Assemble the output byte
    
6. Update MAX using the AND logic
    

The implementation:

```python
def soc(functionList, word):
    hexstring = ""
    maxed=False
    for i in word:
        binstring = ""
        for k in functionList:
            if ((ord(i) in k)^maxed):
                binstring += "1"
            else:
                binstring += "0"
        hexstring += format(int(binstring,2),'02x')
        maxed = (ord(i) in functionList[7]) and (ord(i)&(1))
    return hexstring

print(soc(functionList,"SHAKEITTOTHEMAX"))
```

Here:

```
(ord(i) in k)
```

checks whether the input value belongs to the minterm list for that output.

The XOR with `maxed` flips the logic when MAX is active, effectively switching between **minterms and maxterms**.

---

# Determining the Input Phrase

From the challenge story we know the drones continuously broadcast the song:

```
SHAKE IT TO THE MAX
```

Removing spaces gives:

```
SHAKEITTOTHEMAX
```

Since the swarm communicates using this phrase, it strongly suggests this is the **command phrase to encode**.

---

# Final Step

By feeding

```
SHAKEITTOTHEMAX
```

into the reconstructed encryptor, the program generates the **encrypted hexadecimal message**, which becomes the challenge flag.
