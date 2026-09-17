with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if not latest_frame or not latest_frame.frame:
            return GameAction.ACTION1'''

good = '''        if not latest_frame or not latest_frame.frame:
            logger.error("FRAME IS EMPTY OR NONE!")
            return GameAction.ACTION1'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS")
else:
    print("FAILED")
with open('agent.py', 'w') as f:
    f.write(text)
