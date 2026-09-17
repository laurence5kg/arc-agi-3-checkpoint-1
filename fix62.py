with open('agent.py', 'r') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if "h, w = self.agent_footprint[2], self.agent_footprint[3]" in line:
        start_idx = i
    if "logger.warning(f\"No non-bg color found at deadly location! p_y={p_y}" in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_block = '''                        h, w = self.agent_footprint[2], self.agent_footprint[3]
                        scan_y = max(0, p_y - 5)
                        scan_x = max(0, p_x - 5)
                        patch_crop = self.last_grid[scan_y:p_y+h+5, scan_x:p_x+w+5]
                        bg = getattr(self, 'background_color', 3)
                        agent_color = self.agent_footprint[4]
                        valid_mask = (patch_crop != bg) & (patch_crop != agent_color)
                        match_pixels = patch_crop[valid_mask]
                        if len(match_pixels) > 0:
                            unique, counts = np.unique(match_pixels, return_counts=True)
                            deadly_color = unique[np.argmax(counts)]
                            if not hasattr(self, 'bad_colors'):
                                self.bad_colors = set()
                            self.bad_colors.add(int(deadly_color))
                            logger.warning(f"Added color {deadly_color} to bad_colors (scanned around {p_y},{p_x})!")
                        else:
                            logger.warning(f"No non-bg color found near agent! p_y={p_y}, p_x={p_x}")\n'''
    lines = lines[:start_idx] + [new_block] + lines[end_idx+3:]
    with open('agent.py', 'w') as f:
        f.writelines(lines)
    print("SUCCESS")
else:
    print(f"FAILED {start_idx} {end_idx}")
