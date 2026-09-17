with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if len(valid) > 0:
            p_color = valid[np.argmax(counts[colors != 0])]
            return np.sum(patch_crop == p_color) >= (ph * pw) * 0.5'''

good = '''        if len(valid) > 0:
            p_color = valid[np.argmax(counts[colors != 0])]
            res = np.sum(patch_crop == p_color) >= (ph * pw) * 0.5
            if not res:
                logger.error(f"_check_patch_at failed: pos={pos}, p_color={p_color}, sum={np.sum(patch_crop == p_color)}, thresh={(ph * pw) * 0.5}")
                logger.error(f"patch_crop:\\n{patch_crop}")
            return res'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
