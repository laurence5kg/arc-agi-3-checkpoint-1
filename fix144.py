with open('agent.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.strip() == "else:" and i+1 < len(lines) and "self.agent_pos = None # Lost tracking" in lines[i+1]:
        lines[i] = "                    else:\n"
        print(f"Fixed else indentation at line {i+1}")

with open('agent.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
