with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        self.ignored_targets = old_ignored'''
good = '''        self.ignored_targets_by_level[curr_lvl] = old_ignored'''
text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
