import os
import re

# The same highly constrained regex pattern
pattern = re.compile(r'!\[([^\]]*)\]\((.*?)\|(\d+)\)')

print("--- DRY RUN INITIATED ---")
print("Scanning for Obsidian image links...\n")

match_count = 0

for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Check line by line to provide exact context
            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                for match in matches:
                    match_count += 1
                    original_text = match.group(0)
                    
                    # Construct the proposed HTML replacement
                    replacement_text = f'<img src="{match.group(2)}" width="{match.group(3)}">'
                    
                    print(f"File: {filepath} (Line {line_num})")
                    print(f"  [-] Original: {original_text}")
                    print(f"  [+] Proposed: {replacement_text}\n")

if match_count == 0:
    print("No matches found. Your markdown files are clear.")
else:
    print(f"Total links found: {match_count}")
    print("--- DRY RUN COMPLETE ---")
