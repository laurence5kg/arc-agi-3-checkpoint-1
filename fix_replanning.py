with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        self.last_grid = None
        self.last_action = None'''

repl = '''        self.last_grid = None
        self.last_action = None
        self.replanning_events = 0'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed replanning_events initialization!")
