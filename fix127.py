with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                            import logging
                            logger = logging.getLogger(__name__)'''

good = '''                            # logger is global'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed logger!")
else:
    print("Could not find block!")
