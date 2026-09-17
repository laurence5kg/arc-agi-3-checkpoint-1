with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

appendix = '''
        if not hasattr(self, 'current_path') or not self.current_path:
            self.current_path = self.get_closest_target_path()
            
        if self.current_path:
            action_name = self.current_path.pop(0)
            action = GameAction[action_name]
        else:
            action = GameAction.RESET
            
        self.old_agent_pos = self.agent_pos
        self.last_action = action
        self.last_grid = current_grid
        return action
'''

text = text + appendix

with open('agent.py', 'w', encoding='utf-8') as f:
    f.write(text)
