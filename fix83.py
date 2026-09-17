with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if np.any(valid_mask):
                p_color = unique[valid_mask][np.argmax(counts[valid_mask])]
                res = np.sum(patch_crop == p_color) >= (ph * pw) * 0.5
                if not res:
                    logger.error(f"_check_patch_at failed: pos={pos}, p_color={p_color}, sum={np.sum(patch_crop == p_color)}, thresh={(ph * pw) * 0.5}")
                return res
            else:
                return True'''

good = '''            if np.any(valid_mask):
                p_color = unique[valid_mask][np.argmax(counts[valid_mask])]
                res = np.sum(patch_crop == p_color) >= (ph * pw) * 0.5
                if not res:
                    logger.error(f"_check_patch_at failed: pos={pos}, p_color={p_color}, sum={np.sum(patch_crop == p_color)}, thresh={(ph * pw) * 0.5}")
                return res
            else:
                return False'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
