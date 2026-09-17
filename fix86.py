with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if is_level_transition and self.agent_pos is not None:
            if not self._check_patch_at(current_grid, patch, self.agent_pos):
                logger.warning(f"Re-localization FAILED on level transition! Forcing agent re-extraction via movement.")
                self.agent_pos = None'''

good = '''        if is_level_transition and self.agent_pos is not None:
            # Recompute bg and wall colors for the NEW frame before patch checking!
            unique_colors, color_counts = np.unique(current_grid, return_counts=True)
            self.bg_color = unique_colors[np.argmax(color_counts)]
            
            # Simple wall color extraction (most common color after bg)
            wall_candidates = unique_colors[unique_colors != self.bg_color]
            if len(wall_candidates) > 0:
                wall_counts = [color_counts[unique_colors == c][0] for c in wall_candidates]
                self.wall_color = wall_candidates[np.argmax(wall_counts)]

            if not self._check_patch_at(current_grid, patch, self.agent_pos):
                logger.warning(f"Re-localization FAILED on level transition! Forcing agent re-extraction via movement.")
                self.agent_pos = None'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
