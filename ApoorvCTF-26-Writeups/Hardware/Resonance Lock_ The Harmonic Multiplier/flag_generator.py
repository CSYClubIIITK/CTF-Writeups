#!/usr/bin/env python3
"""
flag_generator.py — Offline flag verifier for the Harmonix-7 challenge.

Usage:
    python flag_generator.py

The flag is now fixed (not derived from baud timing).
It is returned when the player achieves LOCKED and sends a valid MULT command.
"""

import sys
import config as C


def main():
    print(f"Fixed flag: FLAG:{C.FIXED_FLAG}")


if __name__ == "__main__":
    main()
