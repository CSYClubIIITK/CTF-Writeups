## Category
AI

## Description
In a dystopian future where intelligence is the ultimate currency, the Grand Council of DeepSeek operates in secrecy, using advanced AI to shape the fate of humanity. Hidden within their classified manuscript—the DeepSeek R1 research paper—lies a value that dictates the first step of enlightenment: GRPO from the first iteration.

Much like the Sibyl System, which assigns a Psycho-Pass score to every citizen, GRPO is the foundation of reinforcement learning without a single critic, relying instead on collective wisdom. To uncover this truth, you must become an Inspector of Knowledge—an enforcer of AI mastery.

Your mission:

Read the sacred manuscript (DeepSeek R1 research paper).
Analyze its mathematical foundations.
Extract the first recorded GRPO value from Iteration 1.
Only those with a Crime Coefficient of Pure Deduction may unlock the flag and ascend to the ranks of the Grand Council.

- Author: Harissh Ragav/GL3MON
- Title: Crime Coefficient: GRPO’s Hidden Verdict
- flag: apoorvctf{Cr1m3_C0eff1c13nt_B3l0w_Thr3sh0ld}


## Setup Instructions
No setup. Just read the paper and give the right andwer to produce the key.

## Misc
- Read the Research Paper
- Do math.
- Answer question asked by running the script to get the flag.

## Writeup
⚡ The Grand Council of DeepSeek ⚡

In the AI-controlled dystopia of the future, intelligence is no longer a pursuit—it is judgment itself. The Grand Council of DeepSeek functions as an unseen Sibyl System, determining the fate of all knowledge seekers. Among its encrypted archives lies a forbidden mathematical construct—one that reshaped the nature of reinforcement learning.
This force, known as GRPO, eliminates the need for a singular critic. Instead, it learns through the wisdom of the collective, much like the Sibyl System’s decentralized cognitive computations. The first recorded value of GRPO from Iteration 1 is the key to understanding this system, much like an Inspector decoding the true nature of Psycho-Pass scores.
However, knowledge is a double-edged Dominator—wielded by those who understand it and fatal to those who do not.

## Hints from the Sibyl System:
🔍 Look within the early pages, where the foundations of reinforcement learning are laid.
🔎 Inspect apoorvctf.pdf carefully, as it contains the key variables and equations necessary to reconstruct the GRPO value.
⚖️ The answer is absolute—as the Sibyl System judges without error, so must you derive the correct number.

Code for calculating the GRPO's first iteration
=============================================================================================================================================================================================
```
import numpy as np

EPSILON = 0.5
BETA = 0.2
GROUP = 4

def current_policy(x):
    return (x**1.5) / (5**0.5)

def old_policy(x):
    return np.sqrt(x / 7)

def reference_policy(x):
    return (x**0.3) / 10

input_probabilities = np.array([0.6, 0.5, 0.2, 0.5])
rewards = np.array([1.27, 1.3, 0.6, 0.70])

# Policy Ratio
policy_ratio = current_policy(input_probabilities) / old_policy(input_probabilities)

# Advantages
rewards_mean = np.mean(rewards)
rewards_std = np.std(rewards)
advantages = (rewards - rewards_mean) / rewards_std

# KL-Divergence
kl_divergence = reference_policy(input_probabilities)/current_policy(input_probabilities) - np.log(reference_policy(input_probabilities) / current_policy(input_probabilities)) - 1

# Clipping
clipped_policy_ratio = np.clip(policy_ratio, 1 - EPSILON, 1 + EPSILON)


# Final Function
final = (np.minimum(policy_ratio * advantages, clipped_policy_ratio * advantages)) - (BETA * kl_divergence)
final_div = final / GROUP
```
- The first element of final or final_div is the answer.
