with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if clear_memory:
                logger.warning("Re-localization FAILED on level transition! Forcing agent re-extraction via movement.")
                self.agent_pos = None
                self.agent_footprint = None
                self.current_path = []
                return'''
good = '''            if clear_memory:
                logger.warning("Re-localization FAILED on level transition! Forcing agent re-extraction via movement.")
                self.agent_pos = None
                # DO NOT WIPE agent_footprint here so we can detect shape changes and rotation!
                # self.agent_footprint = None
                self.current_path = []
                return'''
if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Patched clear_memory!")
else:
    print("Could not find block!")
