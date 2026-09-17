with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if clear_memory:
            if hasattr(self, 'pruned_edges'):
                self.pruned_edges.clear()
            old_ignored = set()
            logger.info("Level transition: clearing pruned_edges and ignored_targets.")
        else:
            old_ignored = getattr(self, 'ignored_targets', set()).copy()'''

good = '''        if clear_memory:
            if hasattr(self, 'pruned_edges'):
                self.pruned_edges.clear()
            logger.info("Level transition: clearing pruned_edges.")
            if getattr(self, 'advanced_level', False):
                logger.info("Advanced to next level! Clearing ignored_targets.")
                old_ignored = set()
                self.advanced_level = False
            else:
                logger.info("Death/Reset transition! KEEPING ignored_targets.")
                old_ignored = getattr(self, 'ignored_targets', set()).copy()
        else:
            old_ignored = getattr(self, 'ignored_targets', set()).copy()'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
