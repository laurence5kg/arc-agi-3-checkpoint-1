with open('.venv/Lib/site-packages/arc_agi/base.py', 'r') as f:
    text = f.read()
    start = text.find('def _parse_operation_mode_from_env')
    end = text.find('def _get_anonymous_api_key', start)
    print(text[start:end])
