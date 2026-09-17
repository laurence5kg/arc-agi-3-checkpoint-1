with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if np.sum(diff) > 0:
            ys, xs = np.where(diff)
            r_y, r_max_y = ys.min(), ys.max() + 1
            r_x, r_max_x = xs.min(), xs.max() + 1
            
            # Extract agent footprint
            h, w = r_max_y - r_y, r_max_x - r_x
            patch = grid2[r_y:r_max_y, r_x:r_max_x]'''

good = '''        if np.sum(diff) > 0:
            ys, xs = np.where(diff)
            r_y, r_max_y = ys.min(), ys.max() + 1
            r_x, r_max_x = xs.min(), xs.max() + 1
            
            # Extract agent footprint properly!
            # grid2 has the agent at its NEW position. grid1 has it at its OLD position.
            # Find the most common color in grid2[diff] that is NOT the background color.
            bg = getattr(self, 'background_color', 3)
            diff_colors = grid2[diff]
            unique, counts = np.unique(diff_colors, return_counts=True)
            valid_mask = (unique != bg) & (unique != 0)
            if not np.any(valid_mask):
                valid_mask = (unique != 0)
            if np.any(valid_mask):
                agent_c = unique[valid_mask][np.argmax(counts[valid_mask])]
                # Bounding box of agent_c in grid2 within diff
                ays, axs = np.where((grid2 == agent_c) & diff)
                if len(ays) > 0:
                    r_y, r_max_y = ays.min(), ays.max() + 1
                    r_x, r_max_x = axs.min(), axs.max() + 1
            
            h, w = r_max_y - r_y, r_max_x - r_x
            patch = grid2[r_y:r_max_y, r_x:r_max_x]'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
