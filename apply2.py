import os

with open('agent.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """                                from scipy.ndimage import label
                                labeled_array, num_features = label(changed_mask)
                                if num_features > 0:
                                    max_cc_size = max((labeled_array == i).sum() for i in range(1, num_features + 1))
                                    if max_cc_size > 15:
                                        reacted = True"""

replacement = """                                from scipy.ndimage import label
                                labeled_array, num_features = label(changed_mask)
                                max_cc_size = 0
                                if num_features > 0:
                                    max_cc_size = max((labeled_array == i).sum() for i in range(1, num_features + 1))
                                    if max_cc_size > 5 or changed_mask.sum() > 20:
                                        reacted = True
                                logger.info(f"Target reaction check: max_cc_size={max_cc_size}, total_changed={changed_mask.sum()}")"""

if target in code:
    code = code.replace(target, replacement)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully patched agent.py")
else:
    print("Target not found in agent.py")
