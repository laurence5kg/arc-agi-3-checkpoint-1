with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        self.target_mask = np.zeros_like(grid, dtype=bool)
        for t in self.targets:
            t_min_y, t_max_y, t_min_x, t_max_x, _ = t
            self.target_mask[t_min_y:t_max_y+1, t_min_x:t_max_x+1] = True
            
        self.V = set()'''

repl = '''        self.V = set()'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Removed early target_mask")
else:
    print("Not found 1")

with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target2 = '''        logger.info(f"Target Candidates (Interior Only): {len(self.targets)} found.")'''

repl2 = '''        logger.info(f"Target Candidates (Interior Only): {len(self.targets)} found.")
        self.target_mask = np.zeros_like(grid, dtype=bool)
        for t in self.targets:
            t_min_y, t_max_y, t_min_x, t_max_x, _ = t
            self.target_mask[t_min_y:t_max_y+1, t_min_x:t_max_x+1] = True'''

if target2 in text:
    text = text.replace(target2, repl2)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added late target_mask")
else:
    print("Not found 2")
