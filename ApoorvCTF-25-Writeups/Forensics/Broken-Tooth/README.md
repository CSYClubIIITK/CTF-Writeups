# **Broken-Tooth**

## **Description**  
My buddy **Blackbeard with a Broken Blue Tooth** keeps preaching about being a **sigma**, but I caught him vibing to some **pookie music**. I've captured the packets—help me **bully him** by identifying the song.  

### **Flag Format:**  
```
apoorvctf{artist-song}
```
**Example:**  
- **Song:** *Never Gonna Give You Up - by Rick Astley*  
- **Flag:** `apoorvctf{rick_astley-never_gonna_give_you_up}`  

**Author:** Afdul  
**Flag:** `apoorvctf{billie_eilish-birds_of_a_feather}`  

---

## **Miscellaneous Notes**  
- **RTP Streams won't give you the exact audio** with the correct speed and frequency.  
- **However,** the song was still understandable despite the distortion.  

---

## **Writeup**  

### **Step 1: Filter SBC Packets in Wireshark**  
1. Open **Wireshark**.  
2. Use the following filter to capture only SBC packets:  
   ```
   sbc
   ```
3. Note that each packet contains **7 fragments**.  
4. Extract and combine the data from **each fragment** to reconstruct the full audio.  

---

### **Step 2: Extract Audio Data from Packets**  
1. **Open the Lua console** in Wireshark.  
2. **Run the following script** to extract data from SBC packets:  

```lua
local filename = "output.bin"
local file = assert(io.open(filename, "wb"))        

-- Create a tap listener for SBC packets
local tap = Listener.new("frame", "sbc")

function tap.packet(pinfo, tvb)
    -- Get the entire raw packet
    local raw_data = tvb:bytes():raw()

    if #raw_data > 22 then
        -- Remove the first 22 bytes
        local trimmed_data = raw_data:sub(23)  -- Lua uses 1-based indexing

        if file then
            file:write(trimmed_data)
            file:flush() 
            print("Packet " .. pinfo.number .. ": Written " .. #trimmed_data .. " bytes to " .. filename)
        else
            print("Error: File handle is nil")
        end
    else
        print("Packet " .. pinfo.number .. ": Packet too short (<22 bytes), skipped")
    end
end

function tap.reset()
    print("Processing reset")
end
```

3. **After running the script**, Wireshark will generate `output.bin`.  
4. **Rename** `output.bin` to `output.sbc`.  

---




### **Step 3: Convert SBC to WAV**  
To convert the **SBC** file to a **WAV** file, use the following command in a terminal:  
```bash
ffmpeg -f sbc -i output.sbc -ar 44100 -ac 2 output1.wav
```
- `-f sbc`: Input format is SBC  
- `-i output.sbc`: Input file  
- `-ar 44100`: Set sample rate to **44100 Hz**  
- `-ac 2`: Set number of audio channels to **2**  
- `output1.wav`: Output file  

Now, **play the `output1.wav` file** to hear what **Blackbeard was jamming to!** 🎶  

---

### **Step 4: Listen to the Extracted Audio**  
🎧 **Click the link below to listen to the recovered audio:**  
[Listen to the audio](/output/output.wav)

https://github.com/user-attachments/assets/25c1bb4d-6b1c-40f5-a82c-6b991174cb9b

### **Final Thought:**  
Blud was secretly vibing to **Billie Eilish**... 🤨💀  
