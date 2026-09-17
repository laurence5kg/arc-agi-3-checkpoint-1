with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                if path is not None:
                    if len(path) == 0:
                        path = ['ACTION5']
                    target_paths.append((len(path), path))'''

repl = '''                if path is not None:
                    if len(path) == 0:
                        if getattr(self, 'last_action', None) and self.last_action.name == 'ACTION5':
                            path = ['ACTION6']
                        else:
                            path = ['ACTION5']
                    target_paths.append((len(path), path))'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed action5/action6 logic!")
