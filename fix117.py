with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                self.initial_agent_footprint = self.agent_footprint
                if old_patch is not None and old_patch.shape == new_patch.shape:
                    rot_k = -1'''

good = '''                self.initial_agent_footprint = self.agent_footprint
                if old_patch is not None:
                    if not np.array_equal(old_patch, new_patch):
                        logger.warning("Agent footprint changed (color/rotation)! Clearing pruned edges.")
                        self.pruned_edges = set()
                if old_patch is not None and old_patch.shape == new_patch.shape:
                    rot_k = -1'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed clear pruned edges on footprint change!")
else:
    print("Could not find block!")
