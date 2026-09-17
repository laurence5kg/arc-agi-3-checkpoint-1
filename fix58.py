with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        else:
                            logger.warning(f"No non-bg color found at deadly location!\\npatch_crop:\\n{patch_crop}\\nbg={bg}")'''

good = '''                        else:
                            logger.warning(f"No non-bg color found at deadly location! p_y={p_y}, p_x={p_x}, d_y={d_y}, d_x={d_x}, deadly_y={deadly_y}, deadly_x={deadly_x}\\npatch_crop:\\n{patch_crop}\\nbg={bg}")'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
