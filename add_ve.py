with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        if target_paths:
            target_paths.sort(key=lambda x: x[0])
            return target_paths[0][1]'''

repl = '''        if target_paths:
            target_paths.sort(key=lambda x: x[0])
            return target_paths[0][1]
        
        logger.info(f"V: {self.V}")
        for u in self.V:
            logger.info(f"E[{u}]: {self.E.get(u)}")'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Injected V and E dump!")
