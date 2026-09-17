with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                logger.info(f"Re-localized agent from {getattr(self, 'agent_pos', 'Unknown')} to {(found_y, found_x)}")
                self.agent_pos = (found_y, found_x)
                self.current_path = []'''

repl = '''                logger.info(f"Re-localized agent from {getattr(self, 'agent_pos', 'Unknown')} to {(found_y, found_x)}")
                self.agent_pos = (found_y, found_x)
                self.agent_footprint = (found_y, found_x, h, w, patch)
                self.current_path = []'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated footprint update")
else:
    print("Not found")
