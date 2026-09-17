with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = 'MAX_ACTIONS = 200'
repl = 'MAX_ACTIONS = 2000'

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Increased MAX_ACTIONS to 2000")
else:
    print("Not found")
