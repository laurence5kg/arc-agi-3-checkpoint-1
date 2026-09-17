with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                if self.last_grid is not None:
                    _M = (self.last_grid != current_grid)
                    if hasattr(self, 'playable_manifold'):
                        _M = _M & self.playable_manifold
                    if np.sum(_M) == 0:'''

good = '''                if self.last_grid is not None:
                    _M = (self.last_grid != current_grid)
                    if hasattr(self, 'playable_manifold'):
                        _M = _M & self.playable_manifold
                    logger.info(f"Stuck check: np.sum(_M)={np.sum(_M)}")
                    if np.sum(_M) <= 10: # Allow small animation changes'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
