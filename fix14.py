with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6]:
                if self.last_grid is not None and np.array_equal(self.last_grid, current_grid):'''

good = '''            if getattr(self, 'last_action', None) in [GameAction.ACTION5, GameAction.ACTION6]:
                if self.last_grid is not None:
                    _M = (self.last_grid != current_grid)
                    if hasattr(self, 'playable_manifold'):
                        _M = _M & self.playable_manifold
                    if np.sum(_M) == 0:'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
