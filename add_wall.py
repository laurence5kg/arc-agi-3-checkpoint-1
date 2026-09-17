with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''        passable_mask = (grid != wall_color)'''

repl = '''        passable_mask = (grid != wall_color) & (grid != 5)'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Made 5 a wall")
else:
    print("Not found")
