with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                        if path[0] == opposite.get(self.last_action.name):
                            logger.info(f"Skipping target {i} because it requires reversing last action {self.last_action.name}")
                            continue'''

repl = '''                        if path[0] == opposite.get(self.last_action.name):
                            # Only skip if we ACTUALLY moved last turn. If we collided, we MUST be allowed to reverse!
                            if getattr(self, 'agent_pos', None) != getattr(self, 'old_agent_pos', None):
                                logger.info(f"Skipping target {i} because it requires reversing last action {self.last_action.name}")
                                continue'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed anti-loop logic")
else:
    print("Not found")
