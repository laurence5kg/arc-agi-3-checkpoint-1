with open('agent.py', 'r') as f:
    text = f.read()

text = text.replace('patch_crop:\\n{patch_crop}\\nbg={bg}', 'patch_crop: {patch_crop} bg={bg}')

with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
