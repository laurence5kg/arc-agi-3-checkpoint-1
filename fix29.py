with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        self.ignored_targets = old_ignored.copy()
        logger.info(f"Target Candidates (Interior Only): {len(self.targets)} found. (ignored: {len(self.ignored_targets)})")'''

good = '''        if not clear_memory:
            self.ignored_targets = old_ignored.copy()
        logger.info(f"Target Candidates (Interior Only): {len(self.targets)} found. (ignored: {len(self.ignored_targets)})")'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
