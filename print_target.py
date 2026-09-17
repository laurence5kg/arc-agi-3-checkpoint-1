with open('agent.py', 'r') as f:
    text = f.read()
start = text.find('def get_closest_target_path')
end = text.find('def choose_action', start)
print(text[start:end])
