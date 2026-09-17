with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if getattr(self, 'current_path', []):
            action_name = self.current_path.pop(0)
            self.last_action = GameAction[action_name]
            self.last_grid = current_grid
            return self.last_action
        else:
            actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
            idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
            fallback_action = actions[(idx + 1) % len(actions)]
            self.last_action = fallback_action
            self.last_grid = current_grid
            logger.warning(f"No path found! Falling back to {fallback_action.name}")
            return fallback_action
        
        self.just_finished_calibration = False
        self.old_agent_pos = getattr(self, 'agent_pos', None)
        return self.last_action'''

good = '''        if getattr(self, 'current_path', []):
            action_name = self.current_path.pop(0)
            self.last_action = GameAction[action_name]
        else:
            actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
            idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
            fallback_action = actions[(idx + 1) % len(actions)]
            self.last_action = fallback_action
            logger.warning(f"No path found! Falling back to {fallback_action.name}")

        self.last_grid = current_grid
        self.just_finished_calibration = False
        self.old_agent_pos = getattr(self, 'agent_pos', None)
        return self.last_action'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed choose_action early return!")
else:
    print("Could not find block!")
