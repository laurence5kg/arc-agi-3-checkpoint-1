with open('agent.py', 'r') as f:
    text = f.read()
    
import re
text = re.sub(r'logger\.warning\(f"No non-bg color found at deadly location! patch_crop:.*?bg=\{bg\}"\)', 'logger.warning(f"No non-bg color found at deadly location!")', text, flags=re.DOTALL)

with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
