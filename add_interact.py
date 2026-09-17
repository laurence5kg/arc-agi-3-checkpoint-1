with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''            # 2. Check for unexpected environment dynamics'''

repl = '''            # 2. Check for unexpected environment dynamics
            if self.last_action and self.last_action.name in ('ACTION5', 'ACTION6'):
                if np.sum(M) == 0:
                    logger.info(f"{self.last_action.name} had no effect.")
                    if self.last_action.name == 'ACTION6':
                        # Both interactions failed, ignore the target we are standing on
                        if hasattr(self, 'targets'):
                            for t in self.targets:
                                t_min_y, t_max_y, t_min_x, t_max_x, _ = t
                                r_y, r_x = self.agent_pos
                                h, w = self.agent_footprint[2], self.agent_footprint[3]
                                if not (r_y > t_max_y or r_y + h - 1 < t_min_y or r_x > t_max_x or r_x + w - 1 < t_min_x):
                                    if not hasattr(self, 'ignored_targets'):
                                        self.ignored_targets = set()
                                    self.ignored_targets.add((t_min_y, t_min_x))
                                    logger.info(f"Ignoring target at {(t_min_y, t_min_x)}")'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Injected interaction tracking!")
