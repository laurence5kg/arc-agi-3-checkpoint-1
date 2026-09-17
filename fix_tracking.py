with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = '''            self.calibration_phase = False
            self.action_semantics_discovered = True'''

repl1 = '''            self.calibration_phase = False
            self.action_semantics_discovered = True
            self.just_finished_calibration = True'''

target2 = '''        # Environment dynamics verification and tracking
        if self.last_grid is not None:'''

repl2 = '''        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):'''

target3 = '''        self.old_agent_pos = self.agent_pos
        self.last_action = action
        self.last_grid = current_grid
        return action'''

repl3 = '''        self.just_finished_calibration = False
        self.old_agent_pos = getattr(self, 'agent_pos', None)
        self.last_action = action
        self.last_grid = current_grid
        return action'''

text = text.replace(target1, repl1)
text = text.replace(target2, repl2)
text = text.replace(target3, repl3)

with open('agent.py', 'w', encoding='utf-8') as f:
    f.write(text)
