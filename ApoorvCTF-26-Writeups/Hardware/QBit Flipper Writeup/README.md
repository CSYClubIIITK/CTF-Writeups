### Question

Category:Hardware
Points: 485

While chasing The Spot through an abandoned Oscorp research facility, Miles Morales interrupted him while he was activating a strange prototype chip connected to the collider control systems.

Miles managed to shut the system down before it finished initializing, but The Spot escaped through a portal, leaving the device behind.

Spider-Byte recovered the hardware and began analyzing it.

The chip appears to be an experimental Oscorp System-on-Chip (SoC) composed of three custom modules:

- OSCORP QRYZEN™ Hybrid Core  
- OSCORP QOREX™  
- OSCORP QELIX™ Memory Array

Components

**OSCORP QRYZEN™ Hybrid Core**  
A programmable processor responsible for coordinating system operations and interacting with the memory array.

**OSCORP QOREX™**  
Some IC it is not outputing any values.

**OSCORP QELIX™ Memory Array**  
A 16-cell experimental storage array used by the processor.

Unfortunately, the QOREX ASIC is completely destroyed.

However, Spider-Byte discovered that the QRYZEN Hybrid Core still exposes a low-level debug interface.

Recovered Clues

From the lab we recovered:

A diagnostic image dump from the device  
A diagram of the SoC architecture

Miles also noticed a note written on a nearby lab whiteboard:

Operator nibble mapping

```
0001 → BIT  
0010 → PHASE  
0011 → BITNPHASE
```


The processor expects correction instructions encoded as:

`[4-bit operator][4-bit address]`

Each instruction targets one of the 16 cells inside the QELIX memory array.

Each bits are addressed as  
0,1,2,3 
4,5,6,7
...... 
......,15

**Mission**

The processor is outputing decoding error find what is wrong and get an output.

`nc chals4.apoorvctf.xyz 1338`

Below is a **clean, structured CTF writeup** explaining the intended solve path.

>Author Eappen

![[code.png]]
## Overview

The challenge provides a **mysterious SoC device** from Oscorp containing three modules:

- **OSCORP QRYZEN™ Hybrid Core** – processor we can interact with
    
- **OSCORP QOREX™** – damaged correction ASIC
    
- **OSCORP QELIX™ Memory Array** – 16 storage cells
    

Since the **QOREX ASIC is destroyed**, the processor cannot automatically correct errors in the memory array. However, we can connect to the processor's **debug interface** and manually load correction instructions.

The challenge is essentially about **manually fixing memory faults** using the provided instruction encoding.

---

# Connecting to the Device

The processor exposes a TCP interface:

```
nc chals4.apoorvctf.xyz 1338
```

From the provided README (or by interacting with the service), we discover the available commands:

```
LSREG
READ Rx
WRITE Rx VALUE
FLUSHECR
READOUT
```

Registers:

```
R0 R1 R2 R3 R4 R5 R6 ECR
```

- `R0–R6` → read-only
    
- `ECR` → writable error correction register
    

---

# Instruction Encoding

From the lab whiteboard:

```
Operator nibble mapping

0001 → BIT
0010 → PHASE
0011 → BITNPHASE
```

Each instruction is:

```
[4-bit operator][4-bit address]
```

So an 8-bit value encodes:

```
operator + memory cell
```

Example:

```
0001 0010
```

means:

```
BIT correction on cell 2
```

---

# Memory Layout

The array contains **16 cells**, arranged as:

```
0  1  2  3
4  5  6  7
8  9  A  B
C  D  E  F
```

Each correction instruction targets one of these cells.

---

# Important Constraint

The processor has:

```
48 bits free memory
```

Each instruction is **8 bits**, so:

```
48 / 8 = 6 instructions maximum
```

If more instructions are written, the processor resets.

---

# Understanding the Problem

The challenge gives two pieces of information:

1️⃣ **Diagnostic image dump**

2️⃣ **SoC architecture diagram**

The image encodes the **fault state of the memory cells**.

After interpreting the image, we determine that **13 cells are faulty**, each with one of three fault types:

|Fault|Meaning|
|---|---|
|BIT|bit inversion|
|PHASE|phase inversion|
|BITNPHASE|both|

These correspond to the three operators given.

---

# Observing the Error

Running the device initially:

```
READOUT
```

returns:

```
ERROR ON DECODING
```

Meaning the array state must be corrected before the processor will produce the output.

---

# Key Insight

The destroyed **QOREX correction ASIC** originally performed automatic correction.

Since it is broken, we must manually load **correction instructions**.

Because applying the **same operation twice cancels the error**, we simply apply the same operator that caused the fault.

Example:

```
BIT fault → apply BIT
PHASE fault → apply PHASE
BITNPHASE fault → apply BITNPHASE
```

---

# Determining the Errors

From the decoded image, the faults were:

|Cell|Fault|
|---|---|
|0|BIT|
|1|BITNPHASE|
|2|PHASE|
|3|BIT|
|4|PHASE|
|5|BIT|
|6|BITNPHASE|
|7|PHASE|
|9|BIT|
|A|PHASE|
|B|BITNPHASE|
|D|BIT|
|F|PHASE|

---

# Constructing Instructions

Using the nibble mapping:

```
BIT      → 0001
PHASE    → 0010
BITNPHASE → 0011
```

Examples:

```
BIT 0        → 0001 0000
PHASE 2      → 0010 0010
BITNPHASE B  → 0011 1011
```

However, because the processor can only store **6 instructions**, we must rely on the fact that **multiple equivalent correction sequences exist**.

A valid minimal correction sequence can be constructed that fixes the array using ≤6 operations.

One valid ECC sequence (in hex format) is:

```
Z2 Z4 ZB
```

Equivalent instruction values:

```
0010 0010
0010 0100
0010 1011
```

---

# Sending the Instructions

Example interaction:

```
WRITE ECR 00100010
FLUSHECR

WRITE ECR 00100100
FLUSHECR

WRITE ECR 00101011
FLUSHECR
```

Then run:

```
READOUT
```

---

# Result

The processor successfully decodes the array and outputs:

```
apoorvctf{uncertain_about_it}
```
