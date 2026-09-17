with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        for i in range(1, num_features + 1):
            ys, xs = np.where(labeled == i)
            self.targets.append((int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max()), int(grid[ys[0], xs[0]])))'''

good = '''        for i in range(1, num_features + 1):
            ys, xs = np.where(labeled == i)
            color = int(grid[ys[0], xs[0]])
            if hasattr(self, 'bad_colors') and color in self.bad_colors:
                logger.info(f"Ignoring target of color {color} because it is a known trap.")
                continue
            self.targets.append((int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max()), color))'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
