with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        import numpy as np
                        agent_colors = np.unique(self.agent_footprint[4])
                        valid_mask = (patch_crop != bg) & (~np.isin(patch_crop, agent_colors))'''

good = '''                        import numpy as _np
                        agent_colors = _np.unique(self.agent_footprint[4])
                        valid_mask = (patch_crop != bg) & (~_np.isin(patch_crop, agent_colors))'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
