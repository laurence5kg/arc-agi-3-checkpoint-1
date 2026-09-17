with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

if 'import json' not in text:
    text = "import json\nimport os\n" + text
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added imports")
