with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                        else:
                            logger.warning(f"No non-bg color found near agent! p_y={p_y}, p_x={p_x}")\\n                    except IndexError:\\n                        pass'''
good = '''                        else:
                            logger.warning(f"No non-bg color found near agent! p_y={p_y}, p_x={p_x}")
                    except IndexError:
                        pass'''
text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
