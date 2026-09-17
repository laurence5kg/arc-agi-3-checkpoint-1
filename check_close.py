with open('.venv/Lib/site-packages/arc_agi/base.py', 'r') as f:
    text = f.read()
    start = text.find('def close_scorecard')
    end = text.find('def get_scorecard', start)
    print(text[start:end])
