with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        bg = getattr(self, 'background_color', 3)
                        agent_color = self.agent_footprint[4]
                        valid_mask = (patch_crop != bg) & (patch_crop != agent_color)'''

good = '''                        bg = getattr(self, 'background_color', 3)
                        import numpy as np
                        agent_colors = np.unique(self.agent_footprint[4])
                        valid_mask = (patch_crop != bg) & (~np.isin(patch_crop, agent_colors))'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
