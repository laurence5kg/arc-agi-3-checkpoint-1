with open('.venv/Lib/site-packages/arc_agi/base.py', 'r') as f:
    text = f.read()
    start = text.find('def open_scorecard')
    end = text.find('def create_scorecard', start)
    print(text[start:end])
