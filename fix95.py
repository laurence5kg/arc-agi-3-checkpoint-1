with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                self.agent_footprint = (0, 0, h, w, patch)'''
good = '''                self.agent_footprint = (0, 0, h, w, patch)
                self.initial_agent_footprint = self.agent_footprint'''
if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Patched init!")
else:
    print("Could not find block!")
