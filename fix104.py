with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                    if known_patch is not None:
                        if not np.array_equal(patch_old, known_patch):
                            continue'''

good = '''                    if known_patch is not None:
                        kp_mask = known_patch != getattr(self, 'background_color', 3)
                        po_mask = patch_old != getattr(self, 'background_color', 3)
                        if not np.array_equal(po_mask, kp_mask):
                            continue'''

if bad in text:
    text = text.replace(bad, good)
    with open('agent.py', 'w') as f:
        f.write(text)
    print("Fixed known_patch color!")
else:
    print("Could not find block!")
