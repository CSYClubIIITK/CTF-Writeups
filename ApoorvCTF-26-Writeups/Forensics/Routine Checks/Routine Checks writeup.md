>Challenge: Routine Checks
>Flag: apoorvctf{b1ts_wh1sp3r_1n_th3_l0w3st_b1t}

>Description: Routine system checks were performed on the city’s communication network after reports of instability.
>Operators sent brief messages between nodes to confirm everything was running smoothly.
>Most of the exchanges are ordinary status updates, but one message stands out as… different.

>Files: challenge.pcap

>Solution: 

We are given a .pcap file containing network traffic. As the description says, there are system checks being performed but something unusual has been transmitted. 

Opening the given file with writeshark, we see around ~70 TCP conversations, with routine messages like "System health check: OK" and "Network latency seems stable" etc.

These streams appear normal and contain only small text payloads.

Looking at Statistics → Conversations → TCP, we can compare the amount of data transferred in each stream.

Most conversations contain roughly ~600 bytes, but one conversation stands out with a much larger payload (~6026 bytes).

This unusual size suggests that something different was transmitted in this stream.

### Following the TCP stream:

Instead of readable messages, this stream contains a **large block of binary data**, unlike the other conversations.

The data appears to be a continuous sequence of bits, suggesting that a file may have been transmitted in binary form.

### Extracting the Data

From the TCP stream window:

1. Set Show data as → Raw
2. Copy the stream contents
3. Save it to a file, for example `binary.txt`

### Reconstructing the File

The extracted data represents binary bits, so we convert it back into raw bytes.

```python
with open("binary.txt") as f:
    bits = f.read().strip()

data = int(bits, 2).to_bytes(len(bits)//8, "big")

with open("output.bin","wb") as f:
    f.write(data)

```

This reconstructs the original binary file.

Now, attempting to open the file,  we see it is a corrupted jpg file. 

### Repairing the file:

A valid JPG starts with FF D8,

However this obtained file starts with 3F D8.

Using hexedit to fix the header of the file, 3F -> FF, and saving it.

Then, `mv output.bin output.jpg` we get the image. 

Scanning the image, we get the flag `apoorvctf{this_aint_it_brother}`, which is a false flag!!

Using `steghide extract -sf output.jpg` , we get the flag `apoorvctf{b1ts_wh1sp3r_1n_th3_l0w3st_b1t}`





