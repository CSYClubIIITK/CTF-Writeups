# Ghost Signal: Uchiha’s Cipher

**Authors:** Eappen, jxdann (Elix IIITK)  
**Points:** 500  
**Difficulty:** Medium
**Category:** Hardware
![[Mangekyou_Sharingan_Madara.svg]]
## Description

During the **Fourth Great Cyber War**, an enigmatic entity—rumored to be from the **Uchiha clan**—broadcasted a cryptic serial transmission across the digital battlefield. The intercepted signal, fragmented and modulated at varying speeds, concealed an encrypted message hidden beneath the noise. Was this just a simple transmission, or the key to an impending **digital Genjutsu**?

Your mission was clear: **decode the message before reality blurred into illusion**. The challenge provided a `.fig` file—**naruto.fig**—containing the intercepted signal, structured in **UART format** with embedded start and stop bits. However, there was an additional layer of complexity: the transmission utilized **three different baud rates** to obscure the true content.

Only those who could **observe, decipher, and exploit** would unveil the truth behind the Uchiha’s final message.

**Note:** Flag format is `apoorvctf{key}`

---

**Flag**:`apoorvctf{5er!al_D@t@_L3@k}`
## Solution

Players were provided with:

- A **.fig file** containing the UART signal
- A **Python script** to convert decimal to string
- Clues indicating that the signal was transmitted at **multiple baud rates**

### Steps

1. **Brute-force common baud rates**  
    Systematically testing widely used UART baud rates to identify the correct sequence.
    
2. **Automate baud rate detection**  
    Crafting a MATLAB script to analyze timing intervals and dynamically recover the encoded ASCII characters.
    
3. **Extract the Bitstream**  
    Once the correct baud rates were determined, players had to extract the binary sequence by sampling the signal at the correct intervals.
    
4. **Convert Binary to ASCII**  
    The extracted bitstream was then grouped into **8-bit segments** (assuming **8-N-1** format) and converted to ASCII characters, revealing the hidden message.
    

---
## The Plot

![[naruto.fig]]

## Scripts Used

### **Baud Rate Guessing & ASCII Extraction**

```matlab
figFile = 'naruto.fig';
figHandle = openfig(figFile, 'invisible');

axesHandle = findobj(figHandle, 'Type', 'axes');
stemHandle = findobj(axesHandle, 'Type', 'stem');

if isempty(stemHandle)
    error('No stem plot data found in the figure.');
end

time = double(get(stemHandle, 'XData'));
signal = double(get(stemHandle, 'YData'));

close(figHandle);

baudRate = 9600;
bitDuration = 1 / baudRate;

thresh = (max(signal) + min(signal)) / 2;
binarySignal = double(signal > thresh);

sampleTimes = 0:bitDuration:max(time);
bitStream = interp1(time, binarySignal, sampleTimes, 'previous', 'extrap');

numBitsPerFrame = 10;
numFrames = floor(length(bitStream) / numBitsPerFrame);
charStream = '';

for i = 1:numFrames
    frame = bitStream((i-1)*numBitsPerFrame+1 : i*numBitsPerFrame);
    if frame(1) == 0 && frame(end) == 1
        dataBits = frame(2:9);
        charValue = bin2dec(num2str(dataBits));
        charStream = [charStream, char(charValue)];
    end
end

disp('Extracted Character Stream:');
disp(charStream);
```

### **Automated Script for Extraction**

```matlab
clc; clear; close all;

fig = openfig('uart_ctf_signal.fig', 'invisible');
ax = findobj(fig, 'Type', 'axes');
points = findobj(ax, 'Type', 'stem');

if isempty(points)
    error('No valid plot data found.');
end

time = get(points, 'XData');
signal = get(points, 'YData');

[time, sort_idx] = sort(time);
signal = signal(sort_idx);

time_diffs = diff(time);
estimated_bit_time = median(time_diffs(time_diffs > 0));

recovered_bits = [];
char_buffer = '';
i = 1;

while i <= length(signal)
    if signal(i) == 0
        char_bits = [];
        i = i + 1;
        
        for b = 1:8
            if i <= length(signal)
                char_bits = [char_bits, signal(i)];
                i = i + 1;
            end
        end
        
        if length(char_bits) == 8
            char_code = bin2dec(num2str(char_bits));
            char_buffer = [char_buffer, char(char_code)];
        end
        
        if i <= length(signal)
            i = i + 1;
        end
    else
        i = i + 1;
    end
end

fprintf('Recovered UART Message: %s\n', char_buffer);

if isvalid(fig)
    close(fig);
end
```

### **Output**

```bash
>>untitled3
Recovered UART Message: Wake up to reality.Nothing ever goes as planned in this accursed world.The longer you live, the more 5er!al_D@t@_L3@k you realize that only pain, suffering, and futility exist
>>
```

---

## Code Used to Generate the Plot

```matlab
clc; clear; close all;

key = [ ...
"Wake up to reality.", ...
"Nothing ever goes as planned in this accursed world.", ...
"The longer you live, the more 5er!al_D@t@_L3@k you realize that only pain, suffering, and futility exist." ...
];

baud_rates = [9600, 19200, 38400];

signal = [];
time = [];

current_time = 0;

for i = 1:length(baud_rates)
    baud = baud_rates(i);
    bit_time = 1 / baud;
    text = char(key(i));
    
    for j = 1:length(text)
        char_bin = dec2bin(double(text(j)), 8) - '0';
        
        signal = [signal, 0];
        time = [time, current_time];
        current_time = current_time + bit_time;
        
        for b = 1:8
            signal = [signal, char_bin(b)];
            time = [time, current_time];
            current_time = current_time + bit_time;
        end
        
        signal = [signal, 1];
        time = [time, current_time];
        current_time = current_time + bit_time;
    end
end

figure;
stem(time, signal, 'filled');
xlabel('Time (s)');
ylabel('Signal Level');
title('UART Signal Transmission at Different Baud Rates');
grid on;
legend('UART Data');
```

---

## Final Thoughts

This was the easiest **hardware-based cyber challenge**, yet it encapsulated the essence of **signal interception and decoding**. Electrical, Math, and Physics enthusiasts may have found it straightforward, but it was a great test of whether you could **unveil the truth—or remain ensnared in the Uchiha’s illusion.**

**- Eappen**