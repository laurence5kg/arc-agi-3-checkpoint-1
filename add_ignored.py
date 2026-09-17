with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        target_paths = []
        for (t_min_y, t_max_y, t_min_x, t_max_x, color) in self.targets:'''

repl = '''        if not hasattr(self, 'ignored_targets'):
            self.ignored_targets = set()
            
        target_paths = []
        for (t_min_y, t_max_y, t_min_x, t_max_x, color) in self.targets:
            if (t_min_y, t_min_x) in self.ignored_targets:
                continue'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Injected ignored_targets logic!")
