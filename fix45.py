with open('agent.py', 'r') as f:
    text = f.read()

bad1 = '''        if getattr(latest_frame, 'state', None) == GameState.GAME_OVER:
            logger.warning("Game is OVER! Returning RESET.")
            self.last_action = GameAction.RESET
            return GameAction.RESET'''

good1 = '''        if getattr(latest_frame, 'state', None) == GameState.GAME_OVER:
            logger.warning("Game is OVER! Returning RESET.")
            
            # Figure out what we stepped on to die!
            if getattr(self, 'agent_pos', None) is not None and getattr(self, 'last_action', None) is not None:
                d_y, d_x = self.action_mapping.get(self.last_action.name, (0, 0))
                p_y, p_x = self.agent_pos
                deadly_y, deadly_x = p_y + d_y, p_x + d_x
                if getattr(self, 'last_grid', None) is not None:
                    try:
                        deadly_color = self.last_grid[deadly_y, deadly_x]
                        if not hasattr(self, 'bad_colors'):
                            self.bad_colors = set()
                        self.bad_colors.add(deadly_color)
                        logger.warning(f"Added color {deadly_color} to bad_colors!")
                    except IndexError:
                        pass
            
            self.last_action = GameAction.RESET
            return GameAction.RESET'''

if bad1 in text: text = text.replace(bad1, good1)

with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
