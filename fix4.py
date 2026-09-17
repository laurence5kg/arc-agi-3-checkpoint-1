import re

with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                    self.agent_footprint = (expected_y, expected_x, h, w, new_patch)
                        self.current_path = []
                    else:
                        logger.error(f"Re-localization FAILED and expected pos out of bounds. Aborting.")
                        return'''

good = '''                    self.agent_footprint = (expected_y, expected_x, h, w, new_patch)
                    self.current_path = []
                else:
                    logger.error(f"Re-localization FAILED and expected pos out of bounds. Aborting.")
                    return'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
