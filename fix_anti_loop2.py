with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                    if first_action == opposite.get(self.last_action.name):
                        # Skip the first target and go to the second target!
                        logger.info(f"Skipping target 0 because it requires reversing last action {self.last_action.name}")
                        return target_paths[1][1]'''

repl = '''                    if first_action == opposite.get(self.last_action.name):
                        if getattr(self, 'agent_pos', None) != getattr(self, 'old_agent_pos', None):
                            # Skip the first target and go to the second target!
                            logger.info(f"Skipping target 0 because it requires reversing last action {self.last_action.name}")
                            return target_paths[1][1]'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed anti-loop logic")
else:
    print("Not found")
