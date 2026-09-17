with open('.venv/Lib/site-packages/arc_agi/base.py', 'r') as f:
    text = f.read()
    start = text.find('def create_scorecard')
    end = text.find('def _create_scorecard_no_lock', start)
    print(text[start:end])
