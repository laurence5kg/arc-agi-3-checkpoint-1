with open('agent.py', 'r') as f:
    text = f.read()

import re
text = re.sub(r\"\"\"            if getattr\(self, 'last_action', None\) in \[GameAction\.ACTION5, GameAction\.ACTION6\]:
                # Pick an action that bumps into a wall \(or just ACTION5/6 if they do nothing\)
                if getattr\(self, 'calibration_phase', False\):
                    self\.current_path = \['ACTION5'\] \* \(delay \* 3\) \+ path
                else:
                    self\.current_path = \['ACTION5'\] \+ path
            else:
\"\"\", "", text)

with open('agent.py', 'w') as f:
    f.write(text)
