with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if clear_memory:
            logger.info("Level transition: clearing pruned_edges and ignored_targets.")
            self.pruned_edges = set()
            self.ignored_targets = set()'''

good = '''        if clear_memory:
            logger.info("Level transition: clearing pruned_edges.")
            self.pruned_edges = set()
            if getattr(self, 'advanced_level', False):
                logger.info("Advanced to next level! Clearing ignored_targets.")
                self.ignored_targets = set()
                self.advanced_level = False
            else:
                logger.info("Death/Reset transition! KEEPING ignored_targets.")'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
