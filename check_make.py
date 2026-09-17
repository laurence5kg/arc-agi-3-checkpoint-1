with open('.venv/Lib/site-packages/arc_agi/base.py', 'r') as f:
    text = f.read()
    start = text.find('def make(')
    end = text.find('def _find_local_game(', start)
    print(text[start:end])
