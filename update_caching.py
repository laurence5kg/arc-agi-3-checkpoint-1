with open('agent.py', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = '''        # GLOBAL CACHING
        self.cache_file = f"action_cache_{self.game_id}.json"
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                cached = json.load(f)
                # Convert list back to tuple for displacements
                self.action_mapping = {k: tuple(v) for k, v in cached.items()}
            logger.info(f"Loaded cached action mapping: {self.action_mapping}")
            self.calibration_phase = False
            self.action_queue = []
            self.just_finished_calibration = True
        else:
            self.action_mapping = {}'''

repl1 = '''        # GLOBAL CACHING
        self.cache_file = f"action_cache_{self.game_id}.json"
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                cached = json.load(f)
                self.action_mapping = {k: tuple(v) for k, v in cached['mapping'].items()}
                patch = np.array(cached['patch'])
                h, w = patch.shape
                # We'll find y, x in the first frame
                self.agent_footprint = (0, 0, h, w, patch)
            logger.info(f"Loaded cached action mapping: {self.action_mapping}")
            self.calibration_phase = False
            self.action_queue = []
            self.just_finished_calibration = True
        else:
            self.action_mapping = {}'''

target2 = '''            logger.info("=== STAGE 2 CALIBRATION COMPLETE ===")
            logger.info(f"Action Semantics Mapping: {self.action_mapping}")
            with open(self.cache_file, 'w') as f:
                json.dump(self.action_mapping, f)'''

repl2 = '''            logger.info("=== STAGE 2 CALIBRATION COMPLETE ===")
            logger.info(f"Action Semantics Mapping: {self.action_mapping}")
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'mapping': self.action_mapping,
                    'patch': self.agent_footprint[4].tolist() if self.agent_footprint else []
                }, f)'''

if target1 in text:
    text = text.replace(target1, repl1)
    text = text.replace(target2, repl2)
    with open('agent.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Updated caching to include patch")
else:
    print("Not found")
