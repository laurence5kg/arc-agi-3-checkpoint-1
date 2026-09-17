with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if not self.current_path:
            self.current_path = self.get_closest_target_path()
            
        if self.current_path:'''

good = '''        if not getattr(self, 'current_path', []):
            self.current_path = self.get_closest_target_path()
            
        if getattr(self, 'current_path', []):'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed current_path init!")
else:
    print("Could not find block!")
