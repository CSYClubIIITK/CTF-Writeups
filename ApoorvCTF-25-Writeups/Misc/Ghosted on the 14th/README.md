# Ghosted on the 14th

## Description

Terrible blog posts.

> **Author:** _NotAProton_

## Solution

The challenge provides a PCAP (packet capture) file that contains network traffic. We need to analyze it to find clues about the deleted blog.

### Step 1: Analyze the PCAP

First, let's extract any readable text from the PCAP file using the strings command:

```bash
strings chall.pcap
```

output:

```
hawk2:hey there,how was ur valentines day
hawk1:It was fire,i wrote a blog on this 172 200 32 81 8080
GET / HTTP/1.1
Host: 172.200.32.81:8080
User-Agent: Mozilla/5.0
Accept: text/html
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 250
<html></html>
hawk2: delete ts bro
hawk1: sed
```

### Step 2: Locate the Blog

We discover an IP address with a port: 172.200.32.81:8080

When we try to access it in a browser, the site appears to be down, confirming it was deleted as mentioned in the conversation.

### Step 3: Check the Wayback Machine

1. Visit the [Wayback Machine](https://archive.org/web/).
2. Enter the URL: `http://172.200.32.81:8080/`.
3. We find a saved version from February 14, 2025.

### Step 4: Examine the Blog

The archived blog contains what appears to be some fine literature, but no immediately visible flag.

![alt text](image-1.png)

### Step 5: Inspect the page source

1. Right-click on the page.
2. Select "View Page Source" or "Inspect".
3. Look for any hidden content or comments.

We see a hidden comment in the source code:

```html
<!--Chat is this real? YXBvb3JjdGZ7MW1fZzAxbmdfMW41YW4zfQ-->
```

### Step 6: Decode the Message

The message appears to be encoded in Base64. Let's decode it:

```bash
echo "YXBvb3JjdGZ7MW1fZzAxbmdfMW41YW4zfQ" | base64 -d
```

output:

```
apoorctf{1m_g01ng_1n5an3}
```

Note: While the flag format appears to be "apoorctf" instead of the expected "apoorvctf". It is reasonable to assume that this was due to the author losing his sanity. The CTF platform accepts both formats of the flag.
