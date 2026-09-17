with open('agent.py', 'r') as f:
    text = f.read()

text = text.replace('    def choose_action(self, frames, latest_frame):', '''    def choose_action(self, frames, latest_frame):
        if not hasattr(self, "_printed_dir"):
            logger.error("DIR(SELF): " + str(dir(self)))
            self._printed_dir = True''')

with open('agent.py', 'w') as f:
    f.write(text)
