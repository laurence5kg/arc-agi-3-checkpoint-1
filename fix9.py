with open('agent.py', 'r') as f:
    text = f.read()

text = text.replace("logger.error('DIR(SELF): ' + str(dir(self)))", "logger.error('REACHED TRACKING BLOCK!')")
with open('agent.py', 'w') as f:
    f.write(text)
