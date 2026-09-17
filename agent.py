import json
import os
import logging
import random
from typing import List, Tuple, Optional
import numpy as np

from agents.agent import Agent
from arcengine import FrameData, GameAction, GameState

logger = logging.getLogger(__name__)

class GeneralAgent(Agent):
    MAX_ACTIONS = 2000

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import random
        random.seed(42)
        self.calibration_phase = True
        self.action_queue = [
            GameAction.ACTION1,
            GameAction.ACTION2,
            GameAction.ACTION3,
            GameAction.ACTION4
        ]
        self.action_idx = 0
        
        self.agent_footprint = None  # (y, x, h, w, patch)
        
        # GLOBAL CACHING
        self.cache_file = f"action_cache_{self.game_id}.json"
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cached = json.load(f)
                    self.action_mapping = {k: tuple(v) for k, v in cached['mapping'].items()}
                    patch = np.array(cached['patch'])
                    h, w = patch.shape
                    # We'll find y, x in the first frame
                    self.agent_footprint = (0, 0, h, w, patch)
                    self.initial_agent_footprint = self.agent_footprint
                logger.info(f"Loaded cached action mapping: {self.action_mapping}")
                self.calibration_phase = False
                self.action_queue = []
                self.just_finished_calibration = True
            else:
                self.action_mapping = {}
        except Exception as e:
            logger.warning(f"Failed to load cache file {self.cache_file}: {e}. Falling back to live calibration.")
            self.action_mapping = {}
            self.calibration_phase = True
            self.action_queue = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
            self.action_idx = 0
            self.agent_footprint = None
        
        self.last_grid = None
        self.last_action = None
        self.replanning_events = 0

    def is_done(self, frames: List[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN

    def extract_grid(self, frame: FrameData) -> np.ndarray:
        grid = np.array(frame.frame)
        if grid.ndim == 3:
            return grid[-1]
        return grid

    def discover_semantics(self, F_old: np.ndarray, F_new: np.ndarray, known_patch: Optional[np.ndarray] = None) -> Tuple[Tuple[int, int], Optional[tuple]]:
        from scipy.ndimage import label
        
        M = (F_old != F_new)
        if np.sum(M) == 0:
            return (0, 0), None

        H, W = F_old.shape
        best_d = (0, 0)
        best_R = None
        best_score = float('inf')

        labeled, num_features = label(M)
        components = []
        for i in range(1, num_features + 1):
            ys, xs = np.where(labeled == i)
            components.append((ys.min(), ys.max(), xs.min(), xs.max()))
            
        candidate_bboxes = list(components)
        for i in range(len(components)):
            for j in range(i+1, len(components)):
                min_y = min(components[i][0], components[j][0])
                max_y = max(components[i][1], components[j][1])
                min_x = min(components[i][2], components[j][2])
                max_x = max(components[i][3], components[j][3])
                candidate_bboxes.append((min_y, max_y, min_x, max_x))

        for (min_y, max_y, min_x, max_x) in candidate_bboxes:
            for dy in range(-max_y + min_y, max_y - min_y + 1):
                for dx in range(-max_x + min_x, max_x - min_x + 1):
                    if dy == 0 and dx == 0:
                        continue

                    h = (max_y - min_y + 1) - abs(dy)
                    w = (max_x - min_x + 1) - abs(dx)

                    if h <= 0 or w <= 0:
                        continue

                    r_y = min_y - min(0, dy)
                    r_x = min_x - min(0, dx)

                    if r_y < 0 or r_x < 0 or r_y + h > H or r_x + w > W:
                        continue
                    if r_y + dy < 0 or r_x + dx < 0 or r_y + h + dy > H or r_x + w + dx > W:
                        continue

                    patch_old = F_old[r_y:r_y+h, r_x:r_x+w]
                    patch_new = F_new[r_y+dy:r_y+h+dy, r_x+dx:r_x+w+dx]

                    if known_patch is not None:
                        kp_mask = known_patch != getattr(self, 'background_color', 3)
                        po_mask = patch_old != getattr(self, 'background_color', 3)
                        if not np.array_equal(po_mask, kp_mask):
                            continue

                    bg = getattr(self, 'background_color', 3)
                    mask_old = patch_old != bg
                    mask_new = patch_new != bg
                    matched = False
                    for k in range(4):
                        if np.array_equal(np.rot90(mask_old, k=-k), mask_new):
                            matched = True
                            break
                    if matched:
                        mask_union = np.zeros_like(M)
                        mask_union[r_y:r_y+h, r_x:r_x+w] = True
                        mask_union[r_y+dy:r_y+h+dy, r_x+dx:r_x+w+dx] = True
                        
                        local_M = np.zeros_like(M)
                        local_M[min_y:max_y+1, min_x:max_x+1] = M[min_y:max_y+1, min_x:max_x+1]
                        
                        if np.all(mask_union[local_M]):
                            score = h * w
                            if score < best_score:
                                best_score = score
                                best_d = (dy, dx)
                                best_R = (r_y, r_x, h, w, patch_old)
        
        return best_d, best_R

    def build_world_model(self, grid: np.ndarray, clear_memory: bool = False):
        from scipy.ndimage import label
        
        # On level transition, clear all learned knowledge. Otherwise preserve it.
        if clear_memory:
            if hasattr(self, 'pruned_edges'):
                self.pruned_edges.clear()
            logger.info("Level transition: clearing pruned_edges.")
        
        if not hasattr(self, 'ignored_targets_by_level'):
            self.ignored_targets_by_level = {}
        curr_lvl = getattr(self, 'levels_completed', 0)
        old_ignored = self.ignored_targets_by_level.get(curr_lvl, set()).copy()
        ignored_targets = old_ignored

        # RE-LOCALIZE
        if getattr(self, 'agent_footprint', None) is not None:
            old_patch = self.agent_footprint[4]
            h, w = old_patch.shape
            H, W = grid.shape
            found_y, found_x = None, None
            found_patch = None
            
            # Search for the patch and its 90, 180, 270 degree rotations
            for k in range(4):
                patch = np.rot90(old_patch, k)
                ph, pw = patch.shape
                for y in range(H - ph + 1):
                    for x in range(W - pw + 1):
                        if np.array_equal(grid[y:y+ph, x:x+pw], patch):
                            found_y, found_x = y, x
                            found_patch = patch
                            break
                    if found_y is not None:
                        break
                if found_y is not None:
                    break
            if found_y is not None:
                logger.info(f"Re-localized agent from {getattr(self, 'agent_pos', 'Unknown')} to {(found_y, found_x)}")
                self.agent_pos = (found_y, found_x)
                
                # Check rotation k
                rot_k = -1
                for k in range(4):
                    if np.array_equal(np.rot90(old_patch, k), found_patch):
                        rot_k = k
                        break
                
                if rot_k != -1 and rot_k != 0 and hasattr(self, 'action_mapping'):
                    logger.warning(f"Agent rotated by {rot_k * 90} degrees! Updating action mapping.")
                    self.pruned_edges = set()
                    new_mapping = {}
                    for act, (dy, dx) in self.action_mapping.items():
                        ndy, ndx = dy, dx
                        for _ in range(rot_k):
                            # np.rot90(patch, 1) is 90 deg counter-clockwise.
                            # So the agent's forward direction rotates 90 deg counter-clockwise.
                            # Math for 90 deg CCW: (x, y) -> (-y, x)? 
                            # Wait! If patch rotates 90 deg CCW, the UP direction (-5, 0) should become LEFT (0, -5).
                            # Let's check: (dy, dx) = (-5, 0).
                            # 90 deg CCW of vector: (dy, dx) -> (-dx, dy).
                            # So (0, -5). This is LEFT! Correct!
                            ndy, ndx = -ndx, ndy
                        new_mapping[act] = (ndy, ndx)
                    self.action_mapping = new_mapping

                self.agent_footprint = (found_y, found_x, found_patch.shape[0], found_patch.shape[1], found_patch)
                
                # Check for collision
                if getattr(self, 'last_agent_pos', None) is not None and getattr(self, 'last_action', None) is not None:
                    d_y, d_x = self.action_mapping.get(self.last_action.name, (0, 0))
                    if d_y != 0 or d_x != 0:
                        p_y, p_x = self.last_agent_pos
                        expected_pos = (p_y + d_y, p_x + d_x)
                        if expected_pos != self.agent_pos:
                            logger.warning(f"Agent collision detected! Expected {expected_pos}, got {self.agent_pos}. Pruned edge.")
                            if not hasattr(self, 'pruned_edges'): self.pruned_edges = set()
                            self.pruned_edges.add(((p_y, p_x), self.last_action.name))
                            self.current_path = []

        else:
            if clear_memory:
                logger.warning("Re-localization FAILED on level transition! Forcing agent re-extraction via movement.")
                self.agent_pos = None
                # DO NOT WIPE agent_footprint here so we can detect shape changes and rotation!
                # self.agent_footprint = None
                self.current_path = []

                return
            else:
                expected_y, expected_x = getattr(self, 'agent_pos', (self.agent_footprint[0], self.agent_footprint[1]))
                if 0 <= expected_y <= H - h and 0 <= expected_x <= W - w:
                    new_patch = grid[expected_y:expected_y+h, expected_x:expected_x+w]
                    logger.warning(f"Re-localization FAILED. Adopting new patch at {(expected_y, expected_x)}.")
                    self.agent_footprint = (expected_y, expected_x, h, w, new_patch)
                    self.current_path = []

                else:
                    logger.error(f"Re-localization FAILED and expected pos out of bounds. Aborting.")
                    return
        
        H, W = grid.shape
        perimeter = np.concatenate([
            grid[0, :], grid[-1, :],
            grid[1:-1, 0], grid[1:-1, -1]
        ])
        wall_color = int(np.argmax(np.bincount(perimeter)))
        self.wall_color = wall_color
        
        passable_mask = (grid != wall_color)
        labeled_passable, _ = label(passable_mask)
        
        r_y, r_x, h, w, _ = self.agent_footprint
        cy, cx = r_y + h // 2, r_x + w // 2
        manifold_id = labeled_passable[cy, cx]
        self.playable_manifold = (labeled_passable == manifold_id)
        
        s_y, s_x = abs(list(self.action_mapping.values())[0][0]), abs(list(self.action_mapping.values())[0][1])
        if s_y == 0: s_y = s_x
        if s_x == 0: s_x = s_y
        if s_y == 0: s_y = 1; s_x = 1
        self.s_y, self.s_x = s_y, s_x
        
        self.V = set()
        self.E = {}
        
        offset_y = r_y % s_y
        offset_x = r_x % s_x
        
        for y in range(offset_y, H - h + 1, s_y):
            for x in range(offset_x, W - w + 1, s_x):
                node_cy, node_cx = y + h // 2, x + w // 2
                if self.playable_manifold[node_cy, node_cx]:
                    self.V.add((y, x))
                    self.E[(y, x)] = {}
                    
        # Initialize pruned edges tracking if not exists; PRESERVE across rebuilds
        if not hasattr(self, 'pruned_edges'):
            self.pruned_edges = set()
        
        # Prune edges that reference nodes no longer in V (level changed)
        self.pruned_edges = {(u, a) for (u, a) in self.pruned_edges if u in self.V}

        for u in self.V:
            for action_name, d in self.action_mapping.items():
                if d == (0, 0): continue
                if (u, action_name) in self.pruned_edges:
                    continue
                v = (u[0] + d[0], u[1] + d[1])
                if v in self.V:
                    self.E[u][action_name] = v
                    
        total_edges = sum(len(edges) for edges in self.E.values())
        logger.info(f"Filtered Graph: |V|={len(self.V)}, |E|={total_edges}")
        
        interior_pixels = grid[self.playable_manifold]
        bg_color = int(np.argmax(np.bincount(interior_pixels)))
        logger.info(f"Detected background color: {bg_color}, wall color: {wall_color}")
        
        mask = (grid != bg_color) & (grid != wall_color) & self.playable_manifold
        curr_y, curr_x = getattr(self, 'agent_pos', None) or (r_y, r_x)
        mask[curr_y:curr_y+h, curr_x:curr_x+w] = False
        
        labeled, num_features = label(mask)
        self.targets = []
        # Restore previously ignored targets so we don't revisit them
        self.ignored_targets_by_level[curr_lvl] = old_ignored.copy()
        for i in range(1, num_features + 1):
            ys, xs = np.where(labeled == i)
            color = int(grid[ys[0], xs[0]])
            if hasattr(self, 'bad_colors') and color in self.bad_colors:
                logger.info(f"Ignoring target of color {color} because it is a known trap.")
                continue
            self.targets.append((int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max()), color))
            
        logger.info(f"Target Candidates (Interior Only): {len(self.targets)} found. (ignored: {len(ignored_targets)})")
        self.target_mask = np.zeros_like(grid, dtype=bool)
        for t in self.targets:
            t_min_y, t_max_y, t_min_x, t_max_x, _ = t
            self.target_mask[t_min_y:t_max_y+1, t_min_x:t_max_x+1] = True

    def astar(self, start, goals):
        import heapq
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current in goals:
                path = []
                while current in came_from:
                    action, prev = came_from[current]
                    path.append(action)
                    current = prev
                path.reverse()
                return path

            if current not in self.E:
                continue

            for action_name, neighbor in self.E[current].items():
                # Penalize moving into any target unless it's our goal
                penalty = 0
                if hasattr(self, 'target_mask') and neighbor not in goals:
                    h, w = self.agent_footprint[2], self.agent_footprint[3]
                    ny, nx = neighbor
                    # If any part of the agent at neighbor touches a target pixel
                    if np.any(self.target_mask[ny:ny+h, nx:nx+w]):
                        penalty = 100
                
                tentative_g = g_score[current] + 1 + penalty
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = (action_name, current)
                    g_score[neighbor] = tentative_g
                    
                    # Heuristic: min manhattan distance to any goal, scaled by step size
                    if goals:
                        s_y, s_x = abs(list(self.action_mapping.values())[0][0]), abs(list(self.action_mapping.values())[0][1])
                        if s_y == 0: s_y = s_x
                        if s_x == 0: s_x = s_y
                        if s_y == 0: s_y = 1; s_x = 1
                        
                        min_h = min((abs(neighbor[0] - g[0])/s_y + abs(neighbor[1] - g[1])/s_x) for g in goals)
                        f_score = tentative_g + min_h
                    else:
                        f_score = tentative_g
                    
                    heapq.heappush(open_set, (f_score, neighbor))
        return None

    def get_closest_target_path(self):
        if not self.targets:
            return None
        
        # Calculate manhattan distance to all targets to prioritize
        if self.agent_pos is None:
            logger.error("AGENT POS IS NONE IN get_closest_target_path!")
            return None
        r_y, r_x = self.agent_pos
        h, w = self.agent_footprint[2], self.agent_footprint[3]
        
        logger.info(f"Finding path from agent_pos={self.agent_pos}")
        if not hasattr(self, 'ignored_targets_by_level'):
            self.ignored_targets_by_level = {}
        curr_lvl = getattr(self, 'levels_completed', 0)
        ignored_targets = self.ignored_targets_by_level.get(curr_lvl, set())
            
        target_paths = []
        for (t_min_y, t_max_y, t_min_x, t_max_x, color) in self.targets:
            if (t_min_y, t_min_x) in ignored_targets:
                continue
            # We want to reach the CENTER of the target
            goal_nodes = set()
            t_cy = (t_min_y + t_max_y) // 2
            t_cx = (t_min_x + t_max_x) // 2
            
            # Find the node in V closest to the target center
            best_dist = float('inf')
            best_node = None
            for (uy, ux) in self.V:
                # agent center
                acy = uy + h // 2
                acx = ux + w // 2
                dist = abs(acy - t_cy) + abs(acx - t_cx)
                if dist < best_dist:
                    best_dist = dist
                    best_node = (uy, ux)
            if best_node:
                goal_nodes.add(best_node)
            
            logger.info(f"Target at y=[{t_min_y},{t_max_y}] x=[{t_min_x},{t_max_x}] color={color} -> goal_nodes: {goal_nodes}")
            if goal_nodes:
                path = self.astar(self.agent_pos, goal_nodes)
                logger.info(f"A* path to {goal_nodes}: {path}")
                if path is not None:
                    if len(path) == 0:
                        logger.warning(f"Agent is already on target at {goal_nodes} but it remains. Stepping off!")
                        import random
                        # Just take a random step to get off the target, so we can re-evaluate and likely step back on it
                        return [random.choice(list(self.action_mapping.keys()))]
                        
                    target_paths.append((len(path), path, (t_min_y, t_max_y, t_min_x, t_max_x, color)))
        
        if target_paths:
            # We want to pick the closest target, but if we just interacted with a target 
            # and the environment changed, we don't want to immediately interact with it again.
            # We can penalize targets that are very close to us if there are other targets available.
            # Wait, no. Let's just sort by length!
            target_paths.sort(key=lambda x: x[0])
            
            # If the closest target is just 1 step away, and we have another target, 
            # maybe we shouldn't immediately reverse our action?
            # Actually, let's prevent reversing the last action!
            if len(target_paths) > 1 and getattr(self, 'last_action', None):
                first_path = target_paths[0][1]
                if len(first_path) > 0:
                    first_action = first_path[0]
                    # If the first action is the opposite of last_action, it means we are walking back
                    opposite = {
                        'ACTION1': 'ACTION2',
                        'ACTION2': 'ACTION1',
                        'ACTION3': 'ACTION4',
                        'ACTION4': 'ACTION3'
                    }
                    if first_action == opposite.get(self.last_action.name):
                        if getattr(self, 'agent_pos', None) != getattr(self, 'old_agent_pos', None):
                            # Skip the first target and go to the second target!
                            logger.info(f"Skipping target 0 because it requires reversing last action {self.last_action.name}")
                            return target_paths[1][1]

            import random
            # With 20% chance, pick the second closest target to break out of local traps
            if len(target_paths) > 1:
                if random.random() < 0.2:
                    logger.info(f"Randomly chose target 1 (dist {target_paths[1][0]}) over target 0 (dist {target_paths[0][0]})")
                    return target_paths[1][1]

            return target_paths[0][1]
        
        logger.info(f"V: {self.V}")
        for u in self.V:
            logger.info(f"E[{u}]: {self.E.get(u)}")
        
        return None


    def _check_patch_at(self, grid, patch, pos):
        py, px = pos
        _, _, ph, pw, patch_array = patch
        
        if py < 0 or py + ph > grid.shape[0] or px < 0 or px + pw > grid.shape[1]:
            return False
            
        patch_crop = grid[py:py+ph, px:px+pw]
        
        colors, counts = np.unique(patch_array, return_counts=True)
        bg = getattr(self, 'background_color', 3)
        valid_mask = (colors != 0) & (colors != bg)
        if not np.any(valid_mask):
            valid_mask = (colors != 0)
        
        valid = colors[valid_mask]
        if len(valid) > 0:
            p_color = patch[4]
            if p_color is None:
                p_color = valid[np.argmax(counts[valid_mask])]
            res = np.sum(patch_crop == p_color) >= (ph * pw) * 0.5
            if not res:
                logger.error(f"_check_patch_at failed: pos={pos}, p_color={p_color}, sum={np.sum(patch_crop == p_color)}, thresh={(ph * pw) * 0.5}")
            return res
        else:
            return True

    def choose_action(self, frames, latest_frame):
        self.last_agent_pos = getattr(self, 'agent_pos', None)
        self.last_agent_footprint = getattr(self, 'agent_footprint', None)
        if not hasattr(self, "_printed_dir"):
            logger.error("DIR(SELF): " + str(dir(self)))
            self._printed_dir = True
        if not hasattr(self, '_printed_dir'):
            logger.error('REACHED TRACKING BLOCK!')
            self._printed_dir = True
        if not latest_frame or not latest_frame.frame:
            logger.error(f"FRAME IS EMPTY OR NONE! state={latest_frame.state if latest_frame else 'None'}")
            self.last_action = GameAction.RESET
            return GameAction.RESET
            
        if getattr(latest_frame, 'state', None) == GameState.GAME_OVER:
            logger.warning("Game is OVER! Returning RESET.")
            
            if getattr(self, 'agent_pos', None) is not None and getattr(self, 'last_action', None) is not None:
                d_y, d_x = self.action_mapping.get(self.last_action.name, (0, 0))
                p_y, p_x = self.agent_pos
                deadly_y, deadly_x = p_y + d_y, p_x + d_x
                if not hasattr(self, 'deadly_nodes_by_level'):
                    self.deadly_nodes_by_level = {}
                curr_lvl = getattr(self, 'levels_completed', 0)
                if not hasattr(self, 'death_delays_by_level'):
                    self.death_delays_by_level = {}
                curr_lvl = getattr(self, 'levels_completed', 0)
                self.death_delays_by_level[curr_lvl] = self.death_delays_by_level.get(curr_lvl, 0) + 1
                logger.warning(f"Incremented death delay for level {curr_lvl} to {self.death_delays_by_level[curr_lvl]}")
                
                # We do NOT mark deadly nodes permanently if it blocks the only path.
                # Instead, we rely on the death delay to shift timing!
            
            if getattr(self, 'current_target', None) is not None:
                self.current_target = None
                self.current_path = []

            
            self.last_action = GameAction.RESET
            return GameAction.RESET
        current_grid = np.array(latest_frame.frame[0])
        
        if getattr(self, 'agent_pos', None) is None and hasattr(self, 'action_mapping') and not getattr(self, 'calibration_phase', False):
            R = None
            if getattr(self, 'last_grid', None) is not None and not np.array_equal(current_grid, self.last_grid):
                kp = self.agent_footprint[4] if hasattr(self, 'agent_footprint') and self.agent_footprint else None
                d, R = self.discover_semantics(self.last_grid, current_grid, known_patch=kp)
            
            if R is not None:
                new_patch = R[4]
                old_patch = self.agent_footprint[4] if hasattr(self, 'agent_footprint') and self.agent_footprint else None
                self.agent_footprint = R
                self.agent_pos = (R[0] + d[0], R[1] + d[1])
                self.initial_agent_footprint = self.agent_footprint
                if old_patch is not None:
                    if not np.array_equal(old_patch, new_patch):
                        logger.warning("Agent footprint changed (color/rotation)! Clearing pruned edges and ignored targets.")
                        self.pruned_edges = set()
                        curr_lvl = getattr(self, 'levels_completed', 0)
                        if hasattr(self, 'ignored_targets_by_level') and curr_lvl in self.ignored_targets_by_level:
                            self.ignored_targets_by_level[curr_lvl].clear()
                if old_patch is not None and old_patch.shape == new_patch.shape:
                    rot_k = -1
                    for k in range(4):
                        if np.array_equal(np.rot90(old_patch, k=-k), new_patch):
                            rot_k = k
                            break
                    if rot_k != -1 and rot_k != 0:
                        logger.warning(f"Agent rotated by {rot_k * 90} degrees! Updating action mapping.")
                        new_mapping = {}
                        for act, (dy, dx) in self.action_mapping.items():
                            ndy, ndx = dy, dx
                            for _ in range(rot_k):
                                ndy, ndx = ndx, -ndy
                            new_mapping[act] = (ndy, ndx)
                        self.action_mapping = new_mapping
                elif old_patch is not None and old_patch.shape != new_patch.shape:
                    logger.warning("Agent shape changed completely! Re-calibrating.")
                    self.calibration_phase = True
                    self.action_queue = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                    self.action_idx = 0
                    self.action_mapping = {}
                    self.agent_footprint = None
                    self.agent_pos = None
                logger.info(f"Recovered Agent Footprint: {R[2]}x{R[3]} at {self.agent_pos}")
                self.last_grid = current_grid
                if not getattr(self, 'calibration_phase', False):
                    self.build_world_model(current_grid, clear_memory=False)
            else:
                actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
                next_action = actions[(idx + 1) % 4]
                logger.info(f"DEBUG: last_action={getattr(self, 'last_action', None)} idx={idx} next={next_action}")
                self.last_grid = current_grid
                self.last_action = next_action
                return next_action
        elif not getattr(self, 'calibration_phase', False):
            # Normal Tracking Loop
            is_normal_move = False
            if hasattr(self, 'agent_pos') and getattr(self, 'agent_pos', None) is not None and getattr(self, 'last_action', None):
                ay, ax = self.agent_pos
                dy, dx = self.action_mapping.get(self.last_action.name, (0, 0))
                expected_y = ay + dy
                expected_x = ax + dx
                self.last_expected_pos = (expected_y, expected_x)
                is_normal_move = self._check_patch_at(current_grid, self.agent_footprint, (expected_y, expected_x))
                if is_normal_move:
                    self.agent_pos = (expected_y, expected_x)
            
            if not is_normal_move:
                if getattr(self, 'agent_pos', None) is not None:
                    ay, ax = self.agent_pos
                    if getattr(self, 'last_action', None) is not None:
                        dy, dx = self.action_mapping.get(self.last_action.name, (0, 0))
                        if dy != 0 or dx != 0:
                            expected_pos = (ay + dy, ax + dx)
                            for _t in getattr(self, 'targets', []):
                                _t_min_y, _t_max_y, _t_min_x, _t_max_x, _ = _t
                                _ey, _ex = expected_pos
                                _h, _w = self.agent_footprint[2], self.agent_footprint[3]
                                if not (_ey + _h - 1 < _t_min_y or _ey > _t_max_y or _ex + _w - 1 < _t_min_x or _ex > _t_max_x):
                                    _curr_lvl = getattr(self, 'levels_completed', 0)
                                    if not hasattr(self, 'ignored_targets_by_level'):
                                        self.ignored_targets_by_level = {}
                                    if _curr_lvl not in self.ignored_targets_by_level:
                                        self.ignored_targets_by_level[_curr_lvl] = set()
                                    self.ignored_targets_by_level[_curr_lvl].add((_t_min_y, _t_min_x))
                                    logger.warning(f"Target at {_t_min_y}, {_t_min_x} rejected agent (or caused lost tracking). Ignoring it.")
                    
                    if self._check_patch_at(current_grid, self.agent_footprint, (ay, ax)):
                        # Agent didn't move (hit a wall)
                        if getattr(self, 'last_action', None) is not None:
                            dy, dx = self.action_mapping.get(self.last_action.name, (0, 0))
                            if dy != 0 or dx != 0:
                                expected_pos = (ay + dy, ax + dx)
                                logger.warning(f"Agent collision detected! Expected {expected_pos}, got {self.agent_pos}. Pruned edge.")
                                if not hasattr(self, 'pruned_edges'): self.pruned_edges = set()
                                self.pruned_edges.add(((ay, ax), self.last_action.name))
                                self.current_path = []
                                
                                for _t in getattr(self, 'targets', []):
                                    _t_min_y, _t_max_y, _t_min_x, _t_max_x, _ = _t
                                    _ey, _ex = expected_pos
                                    _h, _w = self.agent_footprint[2], self.agent_footprint[3]
                                    if not (_ey + _h - 1 < _t_min_y or _ey > _t_max_y or _ex + _w - 1 < _t_min_x or _ex > _t_max_x):
                                        _curr_lvl = getattr(self, 'levels_completed', 0)
                                        if not hasattr(self, 'ignored_targets_by_level'):
                                            self.ignored_targets_by_level = {}
                                        if _curr_lvl not in self.ignored_targets_by_level:
                                            self.ignored_targets_by_level[_curr_lvl] = set()
                                            
                                        # We collided with a target (locked door/goal). We need a state change!
                                        # Forget all other ignored targets so we can revisit state changers.
                                        self.ignored_targets_by_level[_curr_lvl].clear()
                                        
                                        self.ignored_targets_by_level[_curr_lvl].add((_t_min_y, _t_min_x))
                                        logger.warning(f"Target at {_t_min_y}, {_t_min_x} rejected agent. Ignoring it.")
                    else:
                        self.agent_pos = None # Lost tracking
                        self.current_path = [] # FIX: Ensure we don't blindly execute queued actions while lost
            
            if self.agent_pos is None:
                # We lost tracking! We will recover next turn via discover_semantics
                pass

        
        if self.calibration_phase:
            if self.last_grid is not None and self.last_action is not None:
                known = self.agent_footprint[4] if self.agent_footprint else None
                d, R = self.discover_semantics(self.last_grid, current_grid, known_patch=known)
                logger.info(f"Calibration: {self.last_action.name} -> displacement {d}")
                if d != (0, 0):
                    self.action_mapping[self.last_action.name] = d
                    if self.agent_footprint is None and R is not None:
                        self.agent_footprint = R
                        self.agent_pos = (R[0] + d[0], R[1] + d[1])
                        logger.info(f"Detected Agent Footprint: {R[2]}x{R[3]} at ({R[0]}, {R[1]})")
                    elif hasattr(self, 'agent_pos'):
                        self.agent_pos = (self.agent_pos[0] + d[0], self.agent_pos[1] + d[1])
                else:
                    self.action_mapping[self.last_action.name] = (0, 0)
                    logger.info(f"Calibration: {self.last_action.name} resulted in collision or stationary delta.")

            if self.action_idx < len(self.action_queue):
                action = self.action_queue[self.action_idx]
                self.action_idx += 1
                self.last_action = action
                self.last_grid = current_grid
                return action
            
            self.calibration_phase = False
            self.action_semantics_discovered = True
            self.just_finished_calibration = True
            
            logger.info("=== STAGE 2 CALIBRATION COMPLETE ===")
            logger.info(f"Action Semantics Mapping: {self.action_mapping}")
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump({
                        'mapping': self.action_mapping,
                        'patch': self.agent_footprint[4].tolist() if self.agent_footprint else []
                    }, f)
            except Exception as e:
                logger.warning(f"Failed to write cache file {self.cache_file}: {e}. Continuing without caching.")
            self.build_world_model(current_grid)

        if getattr(self, 'just_finished_calibration', False) and self.last_grid is None:
            self.build_world_model(current_grid)

        # Environment dynamics verification and tracking
        if self.last_grid is not None and not getattr(self, 'just_finished_calibration', False):
            M = (self.last_grid != current_grid)
            if hasattr(self, 'playable_manifold'):
                M_play = M & self.playable_manifold
                total_changed = np.sum(M_play)
            else:
                total_changed = np.sum(M)
            total_pixels = M.shape[0] * M.shape[1]
            
            is_level_transition = (total_changed / total_pixels) > 0.3
            
            if not is_level_transition and getattr(self, 'agent_pos', None) is not None and getattr(self, 'last_agent_pos', None) is not None:
                ay, ax = self.agent_pos
                h, w = self.agent_footprint[2], self.agent_footprint[3]
                amin_y, amax_y = ay, ay + h - 1
                amin_x, amax_x = ax, ax + w - 1
                
                for t in getattr(self, 'targets', []):
                    t_min_y, t_max_y, t_min_x, t_max_x, _ = t
                    if not (amax_y < t_min_y or amin_y > t_max_y or amax_x < t_min_x or amin_x > t_max_x):
                          # Calculate overlap area to avoid 1-pixel edge touches (e.g. ls20 adjacencies)
                          iy_min = max(amin_y, t_min_y)
                          iy_max = min(amax_y, t_max_y)
                          ix_min = max(amin_x, t_min_x)
                          ix_max = min(amax_x, t_max_x)
                          overlap_area = max(0, iy_max - iy_min + 1) * max(0, ix_max - ix_min + 1)
                          
                          # Most targets are 5x5 (25). Require at least 4 pixels of overlap.
                          if overlap_area <= 5:
                              continue
                              
                          # Overlaps! Check if it was a normal move
                          if getattr(self, 'agent_pos', None) == getattr(self, 'last_expected_pos', None):
                            # It arrived normally. BUT did the environment react? (e.g. HUD update)
                            reacted = False
                            if getattr(self, 'last_grid', None) is not None:
                                changed_mask = (current_grid != self.last_grid)
                                # Mask out agent footprint (old and new) to ignore physical moves
                                if getattr(self, 'last_agent_pos', None):
                                    ay, ax = self.last_agent_pos
                                    changed_mask[ay:ay+5, ax:ax+5] = False
                                if getattr(self, 'agent_pos', None):
                                    ay, ax = self.agent_pos
                                    changed_mask[ay:ay+5, ax:ax+5] = False
                                    
                                from scipy.ndimage import label
                                labeled_array, num_features = label(changed_mask)
                                max_cc_size = 0
                                if num_features > 0:
                                    max_cc_size = max((labeled_array == i).sum() for i in range(1, num_features + 1))
                                    if max_cc_size > 5 or changed_mask.sum() > 20:
                                        reacted = True
                                logger.info(f"Target reaction check: max_cc_size={max_cc_size}, total_changed={changed_mask.sum()}")
                            
                            if not reacted:
                                if not hasattr(self, 'ignored_targets_by_level'):
                                    self.ignored_targets_by_level = {}
                                curr_lvl = getattr(self, 'levels_completed', 0)
                                if curr_lvl not in self.ignored_targets_by_level:
                                    self.ignored_targets_by_level[curr_lvl] = set()
                                    
                                # Target didn't react, likely a state changer. Forget other targets!
                                self.ignored_targets_by_level[curr_lvl].clear()
                                self.ignored_targets_by_level[curr_lvl].add((t_min_y, t_min_x))
                                
                                logger.info(f"Target at {t_min_y, t_min_x} did not react. Ignoring it for level {curr_lvl}.")
                                if hasattr(self, 'pruned_edges'):
                                    self.pruned_edges.clear()
                                self.current_path = []

                            else:
                                logger.info(f"Target at {t_min_y, t_min_x} REACTED (HUD/env update)! Not ignoring.")
                                # Clear ignored targets since state changed
                                self.ignored_targets_by_level[getattr(self, 'levels_completed', 0)] = set()
                                self.current_path = []

            
        if not getattr(self, 'current_path', []):
            self.current_path = self.get_closest_target_path()
            
        if getattr(self, 'current_path', []):
            action_name = self.current_path.pop(0)
            self.last_action = GameAction[action_name]
        else:
            actions = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
            idx = actions.index(getattr(self, 'last_action', GameAction.ACTION1)) if getattr(self, 'last_action', None) in actions else -1
            fallback_action = actions[(idx + 1) % len(actions)]
            self.last_action = fallback_action
            logger.warning(f"No path found! Falling back to {fallback_action.name}")

        self.last_grid = current_grid
        self.just_finished_calibration = False
        self.old_agent_pos = getattr(self, 'agent_pos', None)
        return self.last_action
