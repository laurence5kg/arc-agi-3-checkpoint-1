with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                if getattr(self, 'last_grid', None) is not None:
                    try:
                        deadly_color = self.last_grid[deadly_y, deadly_x]
                        if not hasattr(self, 'bad_colors'):
                            self.bad_colors = set()
                        self.bad_colors.add(deadly_color)
                        logger.warning(f"Added color {deadly_color} to bad_colors!")
                    except IndexError:
                        pass'''

good = '''                if getattr(self, 'last_grid', None) is not None:
                    try:
                        h, w = self.agent_footprint[2], self.agent_footprint[3]
                        patch_crop = self.last_grid[deadly_y:deadly_y+h, deadly_x:deadly_x+w]
                        bg = getattr(self, 'background_color', 3)
                        valid_mask = (patch_crop != bg) & (patch_crop != 0)
                        match_pixels = patch_crop[valid_mask]
                        if len(match_pixels) > 0:
                            import numpy as np
                            unique, counts = np.unique(match_pixels, return_counts=True)
                            deadly_color = unique[np.argmax(counts)]
                            if not hasattr(self, 'bad_colors'):
                                self.bad_colors = set()
                            self.bad_colors.add(int(deadly_color))
                            logger.warning(f"Added color {deadly_color} to bad_colors!")
                        else:
                            logger.warning("No non-bg color found at deadly location!")
                    except IndexError:
                        pass'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
