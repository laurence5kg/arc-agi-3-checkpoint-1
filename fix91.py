with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                    opposite = {
                        'ACTION1': 'ACTION4',
                        'ACTION4': 'ACTION1',
                        'ACTION2': 'ACTION3',
                        'ACTION3': 'ACTION2'
                    }'''

good = '''                    opposite = {
                        'ACTION1': 'ACTION2',
                        'ACTION2': 'ACTION1',
                        'ACTION3': 'ACTION4',
                        'ACTION4': 'ACTION3'
                    }'''
text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("REVERSED")
