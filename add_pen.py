with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):'''

repl = '''                # Penalize moving into any target unless it's our goal
                penalty = 0
                if hasattr(self, 'target_mask') and neighbor not in goals:
                    h, w = self.agent_footprint[2], self.agent_footprint[3]
                    ny, nx = neighbor
                    # If any part of the agent at neighbor touches a target pixel
                    if np.any(self.target_mask[ny:ny+h, nx:nx+w]):
                        penalty = 100
                
                tentative_g = g_score[current] + 1 + penalty
                if tentative_g < g_score.get(neighbor, float('inf')):'''

if target in text:
    text = text.replace(target, repl)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added penalty to astar")
else:
    print("Not found")
