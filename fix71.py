with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if getattr(latest_frame, 'state', None) == GameState.GAME_OVER:
            logger.warning("Game is OVER! Returning RESET.")'''
good = '''        if getattr(latest_frame, 'state', None) == GameState.GAME_OVER:
            logger.warning("Game is OVER! Returning RESET.")
            if getattr(self, 'current_target', None) is not None:
                if not hasattr(self, 'ignored_targets'):
                    self.ignored_targets = set()
                t_min_y, t_max_y, t_min_x, t_max_x, color = self.current_target
                self.ignored_targets.add((t_min_y, t_min_x))
                logger.warning(f"Added dead-end target to ignored_targets: {self.current_target}")
                self.current_target = None
                self.current_path = []'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
