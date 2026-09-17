with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        patch_crop = grid[py:py+ph, px:px+pw]
        if patch_crop.shape == (ph, pw):
            unique, counts = np.unique(patch_array, return_counts=True)
            valid_mask = (unique != getattr(self, 'bg_color', 0))
            if np.any(valid_mask):
                p_color = unique[valid_mask][np.argmax(counts[valid_mask])]
                res = np.sum(patch_crop == p_color) >= (ph * pw) * 0.5
                if not res:
                    logger.error(f"_check_patch_at failed: pos={pos}, p_color={p_color}, sum={np.sum(patch_crop == p_color)}, thresh={(ph * pw) * 0.5}")
                return res
            else:
                return False
        return False'''

good = '''        patch_crop = grid[py:py+ph, px:px+pw]
        if patch_crop.shape == (ph, pw):
            bg = getattr(self, 'bg_color', 0)
            agent_mask = (patch_array != bg)
            crop_mask = (patch_crop != bg)
            
            # Check if the non-bg shape matches (at least 80% match)
            match_ratio = np.sum(agent_mask == crop_mask) / (ph * pw)
            if match_ratio >= 0.8 and np.any(crop_mask):
                return True
            else:
                # logger.error(f"_check_patch_at failed: pos={pos}, match_ratio={match_ratio}")
                return False
        return False'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
