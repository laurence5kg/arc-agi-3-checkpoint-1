with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                expected_pos = (p_y + d_y, p_x + d_x)
                
                if d_y != 0 or d_x != 0:'''

good = '''                expected_pos = (p_y + d_y, p_x + d_x)
                self.last_expected_pos = expected_pos
                
                if d_y != 0 or d_x != 0:'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed last_expected_pos!")
else:
    print("Could not find block!")
