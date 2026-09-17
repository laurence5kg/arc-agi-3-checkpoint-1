with open('agent.py', 'r') as f:
    text = f.read()

text = text.replace('import numpy as np\n                            unique', 'unique')

with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
