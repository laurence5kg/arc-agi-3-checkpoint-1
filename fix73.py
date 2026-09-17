with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                    if len(path) == 0:
                        if getattr(self, 'last_action', None) and self.last_action.name == 'ACTION5':
                            path = ['ACTION6']
                        else:
                            path = ['ACTION5']
                    target_paths.append((len(path), path))'''

good = '''                    if len(path) == 0:
                        if getattr(self, 'last_action', None) and self.last_action.name == 'ACTION5':
                            path = ['ACTION6']
                        else:
                            path = ['ACTION5']
                    target_paths.append((len(path), path, (t_min_y, t_max_y, t_min_x, t_max_x, color)))'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
