
with open("agent.py", "r") as f:
    text = f.read()
import re
text = re.sub(r"            if getattr\(self, .last_action., None\) in \[GameAction\.ACTION5.*?\n            else:\n", "", text, flags=re.DOTALL)
with open("agent.py", "w") as f:
    f.write(text)

