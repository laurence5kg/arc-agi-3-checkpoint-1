with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        best_d = (0, 0)
        best_R = None
        best_score = -1'''

good = '''        best_d = (0, 0)
        best_R = None
        best_score = float('inf')'''

if bad in text:
    text = text.replace(bad, good)
    print("SUCCESS 1")
else:
    print("FAILED 1")

bad2 = '''                        if np.all(mask_union[local_M]):
                            score = h * w
                            if score > best_score:
                                best_score = score
                                best_d = (dy, dx)
                                best_R = (r_y, r_x, h, w, patch_old)'''

good2 = '''                        if np.all(mask_union[local_M]):
                            score = h * w
                            if score < best_score:
                                best_score = score
                                best_d = (dy, dx)
                                best_R = (r_y, r_x, h, w, patch_old)'''

if bad2 in text:
    text = text.replace(bad2, good2)
    print("SUCCESS 2")
else:
    print("FAILED 2")

with open('agent.py', 'w') as f:
    f.write(text)
