with open('agent.py', 'r') as f:
    text = f.read()

bad = '''                self.current_path = ['ACTION5'] * delay + self.get_closest_target_path()'''
good = '''                path = self.get_closest_target_path()
                if path:
                    self.current_path = ['ACTION5'] * (delay * 3) + path
                else:
                    self.current_path = []'''
text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
print("SUCCESS")
