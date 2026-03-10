import os
import re

# Regex to match all Obsidian image links
pattern = re.compile(r'!\[([^\]]*)\]\(([^|)]+)(?:\|(\d+))?\)')

def replace_with_html(match):
    """Dynamically generates the HTML tag based on whether a width exists."""
    path = match.group(2).strip()
    width = match.group(3)
    
    if width:
        return f'<img src="{path}" width="{width}">'
    else:
        return f'<img src="{path}">'

files_changed = 0

for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Execute the replacement
            new_content = pattern.sub(replace_with_html, content)

            # Write to disk only if changes were made
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"[+] Patched links in: {filepath}")
                files_changed += 1

print(f"\nExecution complete. Modified {files_changed} markdown files.")
