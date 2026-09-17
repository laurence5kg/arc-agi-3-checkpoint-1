with open('agent.py', 'r') as f:
    text = f.read()

start = text.find('# Figure out what we stepped on to die!')
end = text.find('self.last_action = GameAction.RESET', start)
if start != -1 and end != -1:
    text = text[:start] + text[end:]
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Removed bad_colors logic")
else:
    print("Could not find block")
