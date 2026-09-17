with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        p_color = int(stats.mode(patch, axis=None)[0])
        # Only check the dominant color of the agent patch to avoid background noise
        mask = (patch == p_color)
        match = (crop == p_color)
        thresh = mask.sum() * 0.5
        if match[mask].sum() < thresh:
            logger.error(f"_check_patch_at failed: pos={pos}, p_color={p_color}, sum={match[mask].sum()}, thresh={thresh}")
            logger.error(f"patch_crop:\n{crop}")
            return False'''

good = '''        p_color = None
        if len(self.agent_footprint) == 6:
            p_color = self.agent_footprint[5]
        if p_color is None:
            bg = getattr(self, 'background_color', 3)
            # Find the most common color that is NOT the background color
            unique, counts = np.unique(patch, return_counts=True)
            colors = dict(zip(unique, counts))
            if bg in colors:
                del colors[bg]
            if colors:
                p_color = max(colors.items(), key=lambda x: x[1])[0]
            else:
                p_color = int(stats.mode(patch, axis=None)[0])
                
        mask = (patch == p_color)
        match = (crop == p_color)
        thresh = mask.sum() * 0.5
        if match[mask].sum() < thresh:
            return False'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
