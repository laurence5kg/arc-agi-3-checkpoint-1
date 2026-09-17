with open('agent.py', 'r') as f:
    text = f.read()

bad1 = '''        if not latest_frame or not latest_frame.frame:
            logger.error(f"FRAME IS EMPTY OR NONE! state={latest_frame.state if latest_frame else 'None'}")
            return GameAction.ACTION1'''

good1 = '''        if not latest_frame or not latest_frame.frame:
            logger.error(f"FRAME IS EMPTY OR NONE! state={latest_frame.state if latest_frame else 'None'}")
            self.last_action = GameAction.RESET
            return GameAction.RESET
            
        if getattr(latest_frame, 'state', None) == GameState.GAME_OVER:
            logger.warning("Game is OVER! Returning RESET.")
            self.last_action = GameAction.RESET
            return GameAction.RESET'''

bad2 = '''              is_level_transition = (total_changed / total_pixels) > 0.3'''

good2 = '''              is_level_transition = (total_changed / total_pixels) > 0.3
              if getattr(self, 'last_action', None) == GameAction.RESET:
                  is_level_transition = True'''

bad3 = '''        if getattr(self, 'agent_pos', None) is None:
            logger.info("DEBUG: HITTING BOTTOM FALLBACK!")
            return getattr(self, 'last_action', GameAction.ACTION1)'''

good3 = '''        if getattr(self, 'agent_pos', None) is None:
            logger.info("DEBUG: HITTING BOTTOM FALLBACK!")
            if getattr(self, 'last_action', None) == GameAction.RESET:
                self.last_action = GameAction.ACTION1
                return GameAction.ACTION1
            return getattr(self, 'last_action', GameAction.ACTION1)'''

if bad1 in text: text = text.replace(bad1, good1)
if bad2 in text: text = text.replace(bad2, good2)
if bad3 in text: text = text.replace(bad3, good3)

with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
