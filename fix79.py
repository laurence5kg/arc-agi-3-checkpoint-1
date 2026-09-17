with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        logger.info(f"Target Candidates (Interior Only): {len(self.targets)} found. (ignored: {len(self.ignored_targets)})")'''
good = '''        logger.info(f"Target Candidates (Interior Only): {len(self.targets)} found. (ignored: {len(ignored_targets)})")'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
