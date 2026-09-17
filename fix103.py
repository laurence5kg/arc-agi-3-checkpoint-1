with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                    matched = False
                    for k in range(4):
                        if np.array_equal(np.rot90(patch_old, k=-k), patch_new):
                            matched = True
                            break
                    if matched:'''

good = '''                    bg = getattr(self, 'background_color', 3)
                    mask_old = patch_old != bg
                    mask_new = patch_new != bg
                    matched = False
                    for k in range(4):
                        if np.array_equal(np.rot90(mask_old, k=-k), mask_new):
                            matched = True
                            break
                    if matched:'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed discover_semantics color/rotation!")
else:
    print("Could not find block!")
