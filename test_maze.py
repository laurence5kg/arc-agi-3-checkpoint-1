import sys; sys.path.append('../environment_files/ls20/9607627b'); import ls20; import numpy as np;
env = ls20.Ls20()
env._current_level = 1
grid = np.array(env.render().frame[0])
agent = ls20.levels[1].get_sprites_by_tag('sfqyzhzkij')[0]
print(f"Agent at {agent.y}, {agent.x}")

# Find targets
from scipy.ndimage import label
perimeter = np.concatenate([grid[0,:], grid[-1,:], grid[1:-1,0], grid[1:-1,-1]])
wall_color = int(np.argmax(np.bincount(perimeter)))
passable = grid != wall_color
labels, _ = label(passable)
my_label = labels[agent.y+2, agent.x+2]
print(f"Agent manifold ID: {my_label}")
for tag in ['rjlbuycveu', 'rhsxkxzdjz', 'npxgalaybz']:
    s = ls20.levels[1].get_sprites_by_tag(tag)[0]
    print(f"Target {tag} at {s.y}, {s.x}. Manifold ID: {labels[s.y+2, s.x+2]}")

