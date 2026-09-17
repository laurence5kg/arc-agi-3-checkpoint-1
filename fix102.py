with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                    if np.array_equal(patch_old, patch_new):
                        mask_union = np.zeros_like(M)'''

good = '''                    matched = False
                    for k in range(4):
                        if np.array_equal(np.rot90(patch_old, k=-k), patch_new):
                            matched = True
                            break
                    if matched:
                        mask_union = np.zeros_like(M)'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed discover_semantics rotation!")
else:
    print("Could not find block!")
