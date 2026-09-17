with open('agent.py', 'r') as f:
    text = f.read()

text = text.replace('logger.warning(f"No non-bg color found near agent! p_y={p_y}, p_x={p_x}")', 'logger.warning(f"No non-bg color found near agent! p_y={p_y}, p_x={p_x}")\\n                    except IndexError:\\n                        pass')

with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
