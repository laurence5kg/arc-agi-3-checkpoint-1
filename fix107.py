with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                          is_at_goal = False
                          for (uy, ux) in getattr(self, 'V', []):
                              if abs(uy - t_cy) <= h//2 + 5 and abs(ux - t_cx) <= w//2 + 5:
                                  if (uy, ux) == self.agent_pos:
                                      is_at_goal = True
                                      break'''

good = '''                          is_at_goal = False
                          if getattr(self, 'agent_pos', None) is not None:
                              ay, ax = self.agent_pos
                              amin_y, amax_y = ay, ay + h - 1
                              amin_x, amax_x = ax, ax + w - 1
                              if not (amax_y < t_min_y or amin_y > t_max_y or amax_x < t_min_x or amin_x > t_max_x):
                                  if getattr(self, 'agent_pos', None) == getattr(self, 'last_expected_pos', None):
                                      is_at_goal = True'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed is_at_goal!")
else:
    print("Could not find block!")
