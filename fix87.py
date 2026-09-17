with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        wall_color = int(np.argmax(np.bincount(perimeter)))'''
good = '''        wall_color = int(np.argmax(np.bincount(perimeter)))
        self.wall_color = wall_color'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
