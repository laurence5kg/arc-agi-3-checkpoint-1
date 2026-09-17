with open('agent.py', 'r') as f:
    text = f.read()

bad = '''            actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4, GameAction.ACTION5, GameAction.ACTION6]'''

good = '''            actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed actions!")
else:
    print("Could not find block!")
