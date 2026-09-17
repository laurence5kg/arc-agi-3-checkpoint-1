with open('agent.py', 'r') as f:
    text = f.read()

text = text.replace('valid_mask = (patch_crop != bg) & (patch_crop != 0)', 'valid_mask = (patch_crop != bg)')

with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
