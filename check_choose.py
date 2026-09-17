with open('agent.py', 'r') as f:
    text = f.read()
    start = text.find('elif old_patch is not None and old_patch.shape != new_patch.shape')
    end = text.find('if self.calibration_phase:', start)
    print(text[start:end])
