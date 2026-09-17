with open('agent.py', 'r') as f:
    text = f.read()

bad = '''    def _check_patch_at(self, grid, patch, pos):
        py, px = pos
        ph, pw, h, w, p_color = patch
        
        if py < 0 or py + ph > grid.shape[0] or px < 0 or px + pw > grid.shape[1]:
            return False
            
        patch_crop = grid[py:py+ph, px:px+pw]
        
        if p_color is not None:
            return np.sum(patch_crop == p_color) >= (ph * pw) * 0.5
        else:
            return True'''

good = '''    def _check_patch_at(self, grid, patch, pos):
        py, px = pos
        _, _, ph, pw, patch_array = patch
        
        if py < 0 or py + ph > grid.shape[0] or px < 0 or px + pw > grid.shape[1]:
            return False
            
        patch_crop = grid[py:py+ph, px:px+pw]
        
        colors, counts = np.unique(patch_array, return_counts=True)
        valid = colors[colors != 0]
        if len(valid) > 0:
            p_color = valid[np.argmax(counts[colors != 0])]
            return np.sum(patch_crop == p_color) >= (ph * pw) * 0.5
        else:
            return True'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
