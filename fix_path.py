with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''            if goal_nodes:
                path = self.astar(self.agent_pos, goal_nodes)
                logger.info(f"A* path to {goal_nodes}: {path}")
                if path:
                    target_paths.append((len(path), path))'''

repl = '''            if goal_nodes:
                path = self.astar(self.agent_pos, goal_nodes)
                logger.info(f"A* path to {goal_nodes}: {path}")
                if path is not None:
                    if len(path) == 0:
                        path = ['ACTION5']
                    target_paths.append((len(path), path))'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed path==[] bug!")
