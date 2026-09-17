with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        # Agent didn't move (hit a wall)
                        self.last_expected_pos = (ay, ax) # update expected to actual since it failed to move'''

good = '''                        # Agent didn't move (hit a wall)'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed last_expected_pos override!")
else:
    print("Could not find block!")
