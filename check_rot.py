import numpy as np
old_patch = np.array([
    [12, 12, 12, 12, 12],
    [12, 12, 12, 12, 12],
    [9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9],
])
new_patch = np.rot90(old_patch, k=-1)
for k in range(4):
    if np.array_equal(np.rot90(old_patch, k=-k), new_patch):
        print(f"Match at k={k}")
