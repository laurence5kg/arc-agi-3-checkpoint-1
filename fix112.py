with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        valid = colors[valid_mask]
        if len(valid) > 0:
            p_color = valid[np.argmax(counts[valid_mask])]
            res = np.sum(patch_crop == p_color) >= (ph * pw) * 0.5'''

good = '''        valid = colors[valid_mask]
        if len(valid) > 0:
            p_color = patch[4]
            if p_color is None:
                p_color = valid[np.argmax(counts[valid_mask])]
            res = np.sum(patch_crop == p_color) >= (ph * pw) * 0.5'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed _check_patch_at!")
else:
    print("Could not find block!")
