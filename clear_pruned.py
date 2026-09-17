with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        # RE-LOCALIZE
        if getattr(self, 'agent_footprint', None) is not None:'''

repl = '''        # Clear pruned edges because environment changed, new paths might be open!
        if hasattr(self, 'pruned_edges'):
            self.pruned_edges.clear()

        # RE-LOCALIZE
        if getattr(self, 'agent_footprint', None) is not None:'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Cleared pruned edges")
else:
    print("Not found")
