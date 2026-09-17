with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if is_agent:
                continue
                
            self.targets.append((t_min_y, t_max_y, t_min_x, t_max_x, color))'''

good = '''            if is_agent:
                continue
                
            if hasattr(self, 'bad_colors') and color in self.bad_colors:
                logger.info(f"Ignoring target of color {color} because it is a known trap.")
                continue
                
            self.targets.append((t_min_y, t_max_y, t_min_x, t_max_x, color))'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
