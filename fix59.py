with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        h, w = self.agent_footprint[2], self.agent_footprint[3]
                        patch_crop = self.last_grid[deadly_y:deadly_y+h, deadly_x:deadly_x+w]
                        bg = getattr(self, 'background_color', 3)
                        valid_mask = (patch_crop != bg)
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
                            logger.warning(f"No non-bg color found at deadly location! p_y={p_y}, p_x={p_x}, d_y={d_y}, d_x={d_x}, deadly_y={deadly_y}, deadly_x={deadly_x}\\npatch_crop:\\n{patch_crop}\\nbg={bg}")'''

good = '''                        h, w = self.agent_footprint[2], self.agent_footprint[3]
                        # Scan a 15x15 area around the agent's last position
                        scan_y = max(0, p_y - 5)
                        scan_x = max(0, p_x - 5)
                        patch_crop = self.last_grid[scan_y:p_y+h+5, scan_x:p_x+w+5]
                        bg = getattr(self, 'background_color', 3)
                        agent_color = self.agent_footprint[4]
                        valid_mask = (patch_crop != bg) & (patch_crop != agent_color)
                        match_pixels = patch_crop[valid_mask]
                        if len(match_pixels) > 0:
                            import numpy as np
                            unique, counts = np.unique(match_pixels, return_counts=True)
                            deadly_color = unique[np.argmax(counts)]
                            if not hasattr(self, 'bad_colors'):
                                self.bad_colors = set()
                            self.bad_colors.add(int(deadly_color))
                            logger.warning(f"Added color {deadly_color} to bad_colors (scanned around {p_y},{p_x})!")
                        else:
                            logger.warning(f"No non-bg color found near agent! p_y={p_y}, p_x={p_x}")'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
