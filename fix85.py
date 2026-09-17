with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            match_ratio = np.sum(agent_mask == crop_mask) / (ph * pw)
            if match_ratio >= 0.8 and np.any(crop_mask):
                return True'''

good = '''            match_ratio = np.sum(agent_mask == crop_mask) / (ph * pw)
            wall_c = getattr(self, 'wall_color', -1)
            # Find the most common non-bg color in the crop
            unique, counts = np.unique(patch_crop[crop_mask], return_counts=True)
            dominant_color = unique[np.argmax(counts)] if len(unique) > 0 else -1
            
            if match_ratio >= 0.8 and np.any(crop_mask) and dominant_color != wall_c:
                return True'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
