with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if len(target_paths) > 1 and getattr(self, 'last_action', None):
                first_path = target_paths[0][1]
                if len(first_path) > 0:
                    first_action = first_path[0]
                    # If the first action is the opposite of last_action, it means we are walking back
                    opposite = {
                        'ACTION1': 'ACTION2',
                        'ACTION2': 'ACTION1',
                        'ACTION3': 'ACTION4',
                        'ACTION4': 'ACTION3'
                    }
                    if first_action == opposite.get(self.last_action.name):
                        if getattr(self, 'agent_pos', None) != getattr(self, 'old_agent_pos', None):
                            # Skip the first target and go to the second target!
                            logger.info(f"Skipping target 0 because it requires reversing last action {self.last_action.name}")
                            return target_paths[1][1]
            
            best_path = target_paths[0][1]
        
        if best_path:
            self.current_target = best_target
            logger.info(f"Set current_target to {self.current_target}")
        return best_path'''

good = '''            if len(target_paths) > 1 and getattr(self, 'last_action', None):
                first_path = target_paths[0][1]
                if len(first_path) > 0:
                    first_action = first_path[0]
                    opposite = {
                        'ACTION1': 'ACTION2',
                        'ACTION2': 'ACTION1',
                        'ACTION3': 'ACTION4',
                        'ACTION4': 'ACTION3'
                    }
                    if first_action == opposite.get(self.last_action.name):
                        if getattr(self, 'agent_pos', None) != getattr(self, 'old_agent_pos', None):
                            logger.info(f"Skipping target 0 because it requires reversing last action {self.last_action.name}")
                            self.current_target = target_paths[1][2]
                            logger.info(f"Set current_target to {self.current_target}")
                            return target_paths[1][1]
            
            best_path = target_paths[0][1]
            self.current_target = target_paths[0][2]
            logger.info(f"Set current_target to {self.current_target}")
            return best_path
            
        return None'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
