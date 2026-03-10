# solve.gdb — GDB script to extract the flag from the Requiem binary
#
# The decrypted flag lives on the heap in a Vec<u8> between the
# "printing flag....." println and the write_volatile wipe loop.
#
# Usage:  gdb -batch -x solve.gdb ./requiem

set pagination off
set confirm off
set debuginfod enabled off

# Use starti to stop at the very first instruction so we can read the PIE base
starti

# Use Python to reliably get PIE base and set the breakpoint
python
import gdb

# Get the PIE base from info proc mappings
mappings = gdb.execute("info proc mappings", to_string=True)
pie_base = None
for line in mappings.splitlines():
    if "requiem" in line:
        parts = line.strip().split()
        pie_base = int(parts[0], 16)
        break

if pie_base is None:
    # Fallback: parse /proc/pid/maps
    pid = gdb.execute("info inferior", to_string=True)
    import re
    m = re.search(r'process (\d+)', pid)
    if m:
        with open(f"/proc/{m.group(1)}/maps") as f:
            for line in f:
                if "requiem" in line:
                    pie_base = int(line.split("-")[0], 16)
                    break

if pie_base is not None:
    # Offset 0xbacf: right after "printing flag....." println, before the
    # write_volatile wipe loop. The Vec heap ptr is at 0x8(%rsp).
    bp_addr = pie_base + 0xbacf
    gdb.execute(f"break *{hex(bp_addr)}")
    print(f"[*] PIE base: {hex(pie_base)}")
    print(f"[*] Breakpoint set at: {hex(bp_addr)}")
else:
    print("[!] Could not determine PIE base!")
    gdb.execute("quit")
end

continue

# We've hit the breakpoint. The Vec<u8> is on the stack:
#   0x8(%rsp)  = pointer to heap buffer (the decrypted flag bytes)
#   0x10(%rsp) = length (should be 45 = 0x2d)

printf "\n========== FLAG EXTRACTED ==========\n"
x/s *(char**)($rsp + 0x8)
printf "====================================\n\n"

kill
quit
