import re

with open('agent.py', 'r') as f:
    text = f.read()

# Fix build_world_model mess
bad_block = '''        if getattr(self, 'agent_pos', None) is not None:
            patch = self.agent_footprint
            p_y, p_x = self.agent_pos
            
            # 1. Did we move where we expected?
            d_y, d_x = 0, 0
            if getattr(self, 'last_action', None) and hasattr(self, 'action_mapping'):
                d_y, d_x = self.action_mapping.get(self.last_action.name, (0, 0))
                
            expected_pos = (p_y + d_y, p_x + d_x)
            
            if d_y != 0 or d_x != 0:
                if self._check_patch_at(grid, patch, expected_pos):
                    # We moved successfully
                    self.agent_pos = expected_pos
                else:
                        new_patch = grid[expected_y:expected_y+h, expected_x:expected_x+w]
                        logger.warning(f"Re-localization FAILED. Adopting new patch at {(expected_y, expected_x)}.")
                        self.agent_footprint = (expected_y, expected_x, h, w, new_patch)'''

good_block = '''        else:
            if clear_memory:
                logger.warning("Re-localization FAILED on level transition! Forcing agent re-extraction via movement.")
                self.agent_pos = None
                self.agent_footprint = None
                self.current_path = []
                return
            else:
                expected_y, expected_x = getattr(self, 'agent_pos', (self.agent_footprint[0], self.agent_footprint[1]))
                if 0 <= expected_y <= H - h and 0 <= expected_x <= W - w:
                    new_patch = grid[expected_y:expected_y+h, expected_x:expected_x+w]
                    logger.warning(f"Re-localization FAILED. Adopting new patch at {(expected_y, expected_x)}.")
                    self.agent_footprint = (expected_y, expected_x, h, w, new_patch)'''

# Note: text.replace might fail if indentation or exact string doesn't match perfectly. Let's use re.
import sys

# Replace the messy build_world_model code
text = text.replace(bad_block, good_block)

with open('agent.py', 'w') as f:
    f.write(text)

