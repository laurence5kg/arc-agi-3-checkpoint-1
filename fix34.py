with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        valid = colors[colors != 0]
        if len(valid) > 0:
            p_color = valid[np.argmax(counts[colors != 0])]'''

good = '''        bg = getattr(self, 'background_color', 3)
        valid_mask = (colors != 0) & (colors != bg)
        if not np.any(valid_mask):
            valid_mask = (colors != 0)
        
        valid = colors[valid_mask]
        if len(valid) > 0:
            p_color = valid[np.argmax(counts[valid_mask])]'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
