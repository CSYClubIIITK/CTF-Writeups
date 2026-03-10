import os
import re

# Updated Regex:
# Group 1 = alt text
# Group 2 = path (everything up to a pipe or closing parenthesis)
# Group 3 = width (optional, only captures if a pipe exists)
pattern = re.compile(r'!\[([^\]]*)\]\(([^|)]+)(?:\|(\d+))?\)')

print("--- UPDATED DRY RUN INITIATED ---")
print("Scanning for ALL Obsidian image links...\n")

match_count = 0

for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                for match in matches:
                    match_count += 1
                    original_text = match.group(0)
                    
                    path = match.group(2).strip()
                    width = match.group(3)
                    
                    # Construct HTML: include width if it exists, otherwise omit it
                    if width:
                        replacement_text = f'<img src="{path}" width="{width}">'
                    else:
                        replacement_text = f'<img src="{path}">'
                    
                    print(f"File: {filepath} (Line {line_num})")
                    print(f"  [-] Original: {original_text}")
                    print(f"  [+] Proposed: {replacement_text}\n")

if match_count == 0:
    print("No matches found. Your markdown files are clear.")
else:
    print(f"Total links found: {match_count}")
    print("--- DRY RUN COMPLETE ---")
