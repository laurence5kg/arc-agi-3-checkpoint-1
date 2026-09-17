with open('agent.py', 'r') as f:
    text = f.read()

start = text.find('is_at_goal = False')
end = text.find('if is_at_goal:', start)

good = '''is_at_goal = False
                        if getattr(self, 'agent_pos', None) is not None:
                            ay, ax = self.agent_pos
                            amin_y, amax_y = ay, ay + h - 1
                            amin_x, amax_x = ax, ax + w - 1
                            if not (amax_y < t_min_y or amin_y > t_max_y or amax_x < t_min_x or amin_x > t_max_x):
                                if getattr(self, 'agent_pos', None) == getattr(self, 'last_expected_pos', None):
                                    is_at_goal = True
                        '''

text = text[:start] + good + text[end:]
with open('agent.py', 'w') as f:
    f.write(text)
print("Replaced!")
