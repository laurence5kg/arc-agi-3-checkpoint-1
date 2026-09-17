with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        self.s_y, self.s_x = s_y, s_x
        
        self.V = set()'''

repl = '''        self.s_y, self.s_x = s_y, s_x
        
        self.target_mask = np.zeros_like(grid, dtype=bool)
        for t in self.targets:
            t_min_y, t_max_y, t_min_x, t_max_x, _ = t
            self.target_mask[t_min_y:t_max_y+1, t_min_x:t_max_x+1] = True
            
        self.V = set()'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added target_mask")
else:
    print("Not found")
