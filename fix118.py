with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                if rot_k != -1 and rot_k != 0 and hasattr(self, 'action_mapping'):
                    logger.warning(f"Agent rotated by {rot_k * 90} degrees! Updating action mapping.")
                    new_mapping = {}'''

good = '''                if rot_k != -1 and rot_k != 0 and hasattr(self, 'action_mapping'):
                    logger.warning(f"Agent rotated by {rot_k * 90} degrees! Updating action mapping.")
                    self.pruned_edges = set()
                    new_mapping = {}'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed clear pruned edges on rotate!")
else:
    print("Could not find block!")
