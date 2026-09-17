with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        if target_paths:
            target_paths.sort(key=lambda x: x[0])
            return target_paths[0][1]'''

repl = '''        if target_paths:
            # We want to pick the closest target, but if we just interacted with a target 
            # and the environment changed, we don't want to immediately interact with it again.
            # We can penalize targets that are very close to us if there are other targets available.
            # Wait, no. Let's just sort by length!
            target_paths.sort(key=lambda x: x[0])
            
            # If the closest target is just 1 step away, and we have another target, 
            # maybe we shouldn't immediately reverse our action?
            # Actually, let's prevent reversing the last action!
            if len(target_paths) > 1 and getattr(self, 'last_action', None):
                first_path = target_paths[0][1]
                if len(first_path) > 0:
                    first_action = first_path[0]
                    # If the first action is the opposite of last_action, it means we are walking back
                    opposite = {
                        'ACTION1': 'ACTION2',
                        'ACTION2': 'ACTION1',
                        'ACTION3': 'ACTION4',
                        'ACTION4': 'ACTION3'
                    }
                    if first_action == opposite.get(self.last_action.name):
                        # Skip the first target and go to the second target!
                        logger.info(f"Skipping target 0 because it requires reversing last action {self.last_action.name}")
                        return target_paths[1][1]

            return target_paths[0][1]'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added reverse prevention")
else:
    print("Not found")
