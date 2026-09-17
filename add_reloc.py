with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''    def build_world_model(self, grid: np.ndarray):
        from scipy.ndimage import label'''

repl = '''    def build_world_model(self, grid: np.ndarray):
        from scipy.ndimage import label
        
        # RE-LOCALIZE
        if getattr(self, 'agent_footprint', None) is not None:
            patch = self.agent_footprint[4]
            h, w = patch.shape
            H, W = grid.shape
            found_y, found_x = None, None
            for y in range(H - h + 1):
                for x in range(W - w + 1):
                    if np.array_equal(grid[y:y+h, x:x+w], patch):
                        found_y, found_x = y, x
                        break
                if found_y is not None:
                    break
            if found_y is not None:
                logger.info(f"Re-localized agent from {getattr(self, 'agent_pos', 'Unknown')} to {(found_y, found_x)}")
                self.agent_pos = (found_y, found_x)
                self.current_path = []'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added re-localization")
else:
    print("Not found")
