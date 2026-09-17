with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                            logger.warning("No non-bg color found at deadly location!")'''

good = '''                            logger.warning(f"No non-bg color found at deadly location! patch_crop:\n{patch_crop}\nbg={bg}")'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
