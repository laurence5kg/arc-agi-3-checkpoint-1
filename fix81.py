with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        old_ignored = self.ignored_targets_by_level.get(curr_lvl, set()).copy()'''
good = '''        old_ignored = self.ignored_targets_by_level.get(curr_lvl, set()).copy()
        ignored_targets = old_ignored'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
