import os

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """                          # Most targets are 5x5 (25). Require at least 4 pixels of overlap.
                          if overlap_area < 4:"""

replacement = """                          # Most targets are 5x5 (25). Require at least 4 pixels of overlap.
                          if overlap_area <= 5:"""

if target in code:
    code = code.replace(target, replacement)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully patched agent.py")
else:
    print("Target not found in agent.py")
