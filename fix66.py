with open('agent.py', 'r') as f:
    text = f.read()

text = text.replace('import numpy as np\\n                            unique, counts = np.unique(match_pixels, return_counts=True)', 'unique, counts = np.unique(match_pixels, return_counts=True)')

with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
