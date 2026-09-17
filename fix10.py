with open('agent.py', 'r') as f:
    text = f.read()

# 1. Define _check_patch_at inside GeneralAgent class
check_patch_code = '''
    def _check_patch_at(self, grid, patch, pos):
        py, px = pos
        ph, pw, h, w, p_color = patch
        
        if py < 0 or py + ph > grid.shape[0] or px < 0 or px + pw > grid.shape[1]:
            return False
            
        patch_crop = grid[py:py+ph, px:px+pw]
        
        if p_color is not None:
            return np.sum(patch_crop == p_color) >= (ph * pw) * 0.5
        else:
            return True
'''

if 'def _check_patch_at' not in text:
    text = text.replace('    def choose_action(', check_patch_code + '\n    def choose_action(')

# 2. Fix just_finished_calibration so it resets correctly
# We should reset it right after the tracking block finishes
bad_tracking_end = '''            elif total_changed > 0 and not getattr(self, 'environment_changed', False):
                # If only environment changed, not handled by collision or re-localization
                # wait, if agent moved, M > 0.
                pass # Only replan on level transition or collision/re-localization'''

good_tracking_end = '''            elif total_changed > 0 and not getattr(self, 'environment_changed', False):
                pass
        
        # Always reset these after tracking
        self.just_finished_calibration = False
        self.old_agent_pos = getattr(self, 'agent_pos', None)'''

text = text.replace(bad_tracking_end, good_tracking_end)

with open('agent.py', 'w') as f:
    f.write(text)
