with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            total_pixels = M.shape[0] * M.shape[1]
            
                self.current_path = self.get_closest_target_path()
            
        if self.current_path:'''

good = '''            total_pixels = M.shape[0] * M.shape[1]
            
        if not self.current_path:
            self.current_path = self.get_closest_target_path()
            
        if self.current_path:'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed indentation!")
else:
    print("Could not find block!")
