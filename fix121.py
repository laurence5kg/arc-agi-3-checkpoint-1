with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        if getattr(self, 'last_action', None) and self.last_action.name == 'ACTION5':
                            path = ['ACTION6']
                        else:
                            path = ['ACTION5']'''

good = '''                        path = ['ACTION1']'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed zero length path action!")
else:
    print("Could not find block!")
