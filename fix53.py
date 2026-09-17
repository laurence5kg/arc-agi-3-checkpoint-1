with open('agent.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "No non-bg color found at deadly location" in line:
        lines[i] = "                            logger.warning(f\"No non-bg color found at deadly location! patch_crop: {patch_crop} bg={bg}\")\n"

with open('agent.py', 'w') as f:
    f.writelines(lines)
print("SUCCESS")
