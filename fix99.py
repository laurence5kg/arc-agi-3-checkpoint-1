with open('agent.py', 'r') as f:
    text = f.read()
bad = '''                if old_patch is not None and old_patch.shape == new_patch.shape:
                    import numpy as np
                    rot_k = -1'''
good = '''                if old_patch is not None and old_patch.shape == new_patch.shape:
                    rot_k = -1'''
if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed UnboundLocalError!")
else:
    print("Could not find block!")
