with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """                                    _ey, _ex = expected_pos
                                    if _t_min_y <= _ey <= _t_max_y and _t_min_x <= _ex <= _t_max_x:"""

replacement = """                                    _ey, _ex = expected_pos
                                    _h, _w = self.agent_footprint[2], self.agent_footprint[3]
                                    if not (_ey + _h - 1 < _t_min_y or _ey > _t_max_y or _ex + _w - 1 < _t_min_x or _ex > _t_max_x):"""

if target in code:
    code = code.replace(target, replacement)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully patched agent.py")
else:
    print("Target not found in agent.py")
