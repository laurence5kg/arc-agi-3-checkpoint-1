with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        if self._check_patch_at(current_grid, patch, (p_y, p_x)):
                            logger.warning(f"Agent collision detected! Pruned edge {self.last_action.name} from {self.agent_pos}")'''

good = '''                        if self._check_patch_at(current_grid, patch, (p_y, p_x)):
                            logger.warning(f"Agent collision detected! Pruned edge {self.last_action.name} from {self.agent_pos}")
                            self.mechanic_triggered = True'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed mechanic collision!")
else:
    print("Could not find block!")
