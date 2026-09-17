with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        self.targets = []
        for i in range(1, num_features + 1):'''

repl = '''        self.targets = []
        self.ignored_targets = set()
        for i in range(1, num_features + 1):'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed ignored_targets clearing!")
