with open('agent.py', 'r') as f:
    text = f.read()

start = text.find('is_at_goal = False')
end = text.find('if is_at_goal:', start)
print(text[start:end])
