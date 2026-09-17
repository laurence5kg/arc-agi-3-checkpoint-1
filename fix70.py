with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        return best_path'''
good = '''        if best_path:
            self.current_target = best_target
        return best_path'''
text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
