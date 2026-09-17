with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        curr_y, curr_x = getattr(self, 'agent_pos', (r_y, r_x))'''

good = '''        curr_y, curr_x = getattr(self, 'agent_pos', None) or (r_y, r_x)'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
