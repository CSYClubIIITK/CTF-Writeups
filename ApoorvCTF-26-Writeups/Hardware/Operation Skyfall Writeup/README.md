# CLASSIFIED — OPERATION SKYFALL

### INTEL DIVISION / SIGNALS BRANCH / EYES ONLY

---

```
 ██████╗ ██████╗ ███████╗██████╗  █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
██║   ██║██████╔╝█████╗  ██████╔╝███████║   ██║   ██║██║   ██║██╔██╗ ██║
██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
╚██████╔╝██║     ███████╗██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

            ███████╗██╗  ██╗██╗   ██╗███████╗ █████╗ ██╗     ██╗
            ██╔════╝██║ ██╔╝╚██╗ ██╔╝██╔════╝██╔══██╗██║     ██║
            ███████╗█████╔╝  ╚████╔╝ █████╗  ███████║██║     ██║
            ╚════██║██╔═██╗   ╚██╔╝  ██╔══╝  ██╔══██║██║     ██║
            ███████║██║  ██╗   ██║   ██║     ██║  ██║███████╗███████╗
            ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
```

---

### MISSION DOSSIER

**Classification:** TOP SECRET // SIGINT // NOFORN

**Date:** 2026-03-07

**Operational Unit:** GCHQ Joint Cyber Division — Sports Integrity Taskforce

**Case Number:** SIT-2026-0441

---

### BACKGROUND

For the past eighteen months, the Sports Integrity Taskforce has been tracking an anomalous RF signal originating from the vicinity of the Etihad Stadium, Manchester, United Kingdom. The transmission occurs exclusively during home fixtures and does not correlate with any licensed broadcasting, stadium communications, or emergency band activity.

Three weeks ago, an undercover operative embedded within the stadium's technical operations staff confirmed the source: a modified sub-GHz transceiver concealed inside a custom earpiece worn by a member of the coaching staff. Financial intelligence suggests a parallel operation — an offshore auction house based in the Cayman Islands has been placing statistically impossible wagers on in-game events, timed with precision that suggests real-time insider communication.

The transceiver hardware was visually identified but not recovered. Based on physical dimensions, antenna characteristics, and the operating frequency observed on a nearby spectrum analyser, the device is believed to use a commercially available ISM-band radio IC commonly deployed in industrial telemetry, remote keyless entry, and smart metering systems.

### THE INTERCEPT

On matchday, our signals team deployed a wideband SDR receiver in a surveillance vehicle 300 metres from the stadium. A single IQ capture was obtained covering a brief window of the transmission.

The recording contains what analysts believe to be **two distinct transmission bursts** at different points in time. Beyond that, no further analysis has been completed. The field team was compromised and had to extract before they could process the capture.

**The raw IQ file is all we have.**

### YOUR ORDERS

You are a signals analyst. Your mission is straightforward:

1. Determine the nature of the intercepted signals.
2. Extract any intelligence contained within.
3. Recover the flag.

You are provided with **one file**. Nothing else. No metadata logs, no analyst notes, no preliminary reports. The field team left in a hurry.

### WHAT WE KNOW (operationally verified)

- The capture was recorded with a **wideband SDR** using complex float32 format.
- The recording duration is approximately **4 seconds**.
- The operating band is believed to be the **433 MHz ISM band** — popular for unlicensed sub-GHz devices in Europe.
- There are **two separate transmissions** in the capture. Their relationship is unknown.

**That is all.**

### WHAT WE DO NOT KNOW

- The modulation scheme(s) used.
- The data encoding.
- The symbol rate(s).
- The packet structure or protocol.
- Whether the signals are related to each other.
- The sample rate of the capture (the field team's SDR configuration was not logged before extraction).

### ATTACHMENT

| File | Description |
|------|-------------|
| `challenge_2048k_cf32.iq` | Raw IQ intercept — complex float32, interleaved I/Q, little-endian |

The filename may or may not contain useful information. Trust nothing. Verify everything.

### FLAG FORMAT

```
apoorvctf{...}
```

### RULES OF ENGAGEMENT

- You will receive no further intelligence updates.
- You may use any analysis tools at your disposal.
- There are no hints.

---

*"The signal is the truth. Everything else is noise."*

— GCHQ SIGINT Doctrine, Chapter 4

---

**END OF DOSSIER**

**CLASSIFICATION: TOP SECRET // SIGINT // NOFORN**
