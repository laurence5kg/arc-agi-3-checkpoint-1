with open('agent.py', 'r') as f:
    text = f.read()

bad = '''        if target_paths:
            # We want to pick the closest target, but if we just interacted with a target 
            # and the environment changed, we don't want to immediately interact with it again.
            # We can penalize targets that are very close to us if there are other targets available.
            # Wait, no. Let's just sort by length!
            target_paths.sort(key=lambda x: x[0])
            
            return target_paths[0][1]'''

good = '''        if target_paths:
            # We want to pick the closest target, but if we just interacted with a target 
            # and the environment changed, we don't want to immediately interact with it again.
            # We can penalize targets that are very close to us if there are other targets available.
            # Wait, no. Let's just sort by length!
            target_paths.sort(key=lambda x: x[0])
            logger.info(f"Target paths: {target_paths}")
            return target_paths[0][1]'''

text = text.replace(bad, good)
with open('agent.py', 'w') as f:
    f.write(text)
