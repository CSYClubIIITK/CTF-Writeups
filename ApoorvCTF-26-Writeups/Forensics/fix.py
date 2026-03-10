import os
import re

# This regex finds: ![image](Attachments/Pasted image...png|290)
# Group 1 = alt text, Group 2 = file path, Group 3 = width
pattern = re.compile(r'!\[([^\]]*)\]\((.*?)\|(\d+)\)')

for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Swap Obsidian syntax for GitHub HTML
            new_content = pattern.sub(r'<img src="\2" width="\3">', content)

            # Write changes if the file needed fixing
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"[+] Fixed links in: {filepath}")

print("Done hunting down those links!")
