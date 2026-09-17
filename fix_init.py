with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):'''

repl = '''        if getattr(self, 'just_finished_calibration', False) and self.last_grid is None:
            self.build_world_model(current_grid)

        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed initial build_world_model")
else:
    print("Not found")
