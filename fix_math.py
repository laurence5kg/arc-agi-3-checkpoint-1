with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                    if self.agent_footprint is None and R is not None:
                        self.agent_footprint = R
                        self.agent_pos = (R[0], R[1])'''

repl = '''                    if self.agent_footprint is None and R is not None:
                        self.agent_footprint = R
                        self.agent_pos = (R[0] + d[0], R[1] + d[1])'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed agent_pos update!")
