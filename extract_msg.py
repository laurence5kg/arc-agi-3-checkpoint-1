import json

with open('C:/Users/27073/.gemini/antigravity/brain/530bd8a9-1d1c-440d-9223-c30a77ca9b32/.system_generated/logs/transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'PLANNER_RESPONSE' and data.get('tool_calls'):
            for call in data['tool_calls']:
                if call['name'] == 'send_message':
                    msg = call['args']['Message']
                    if 'LEVELS =' in msg:
                        # Extract just Level 1 (which is index 0)
                        start = msg.find('1: {')
                        end = msg.find('2: {')
                        print(msg[start:end])
                        import sys
                        sys.exit(0)
