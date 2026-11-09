"""Pure observed-history model tools, embedded inside the existing child runner.

Model source runs only in that child. No engine, filesystem, network, or action
callback is supplied to its namespace. This reuses the reference isolation; it
does not claim to turn Python into an adversarial security boundary.
"""
import ast
import builtins
import copy
import contextlib
import hashlib
import heapq
import json
import math
import signal
import time
import types


class _PlannerTimeout(BaseException):
    pass


@contextlib.contextmanager
def _planner_budget(seconds):
    # The competition child runs on POSIX, on its main thread. Windows CPU
    # checks use cooperative bounds plus the runner's outer wall timeout.
    if not hasattr(signal, 'setitimer'):
        yield
        return
    def interrupt(signum, frame):
        raise _PlannerTimeout()
    previous = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, 0)
    started = time.monotonic()
    signal.signal(signal.SIGALRM, interrupt)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        if previous_timer[0] > 0:
            signal.setitimer(signal.ITIMER_REAL, max(.001, previous_timer[0]-(time.monotonic()-started)), previous_timer[1])


def fingerprint(frame):
    return hashlib.sha256(json.dumps(frame.get('grid', []), separators=(',', ':')).encode()).hexdigest()


def binding(frame, version):
    return {'model_version': version, 'level': frame.get('level'), 'action_index': frame.get('step'),
            'observation_fingerprint': fingerprint(frame)}


def transition_id(frame):
    return f"L{frame.get('level')}:A{frame.get('step')}"


def compare_grid(predicted, observed):
    if not isinstance(predicted, (list, tuple)) or len(predicted) != len(observed):
        return {'claimed': 0, 'total': sum(map(len, observed)), 'correct': 0, 'shape_error': True}
    claimed = correct = total = 0
    for p_row, o_row in zip(predicted, observed):
        if not isinstance(p_row, (list, tuple)) or len(p_row) != len(o_row):
            return {'claimed': claimed, 'total': sum(map(len, observed)), 'correct': correct, 'shape_error': True}
        for p, o in zip(p_row, o_row):
            total += 1
            if p is not None:
                if isinstance(p, str) and len(p) == 1 and p in 'WwgGcBMPRbSYOrNp':
                    p = 'WwgGcBMPRbSYOrNp'.index(p)
                if type(p) is not int or not 0 <= p <= 15:
                    raise ValueError('render cells must be ARC symbols, 0..15, or None')
                claimed += 1
                correct += int(p == o)
    return {'claimed': claimed, 'total': total, 'correct': correct, 'shape_error': False}


def observed_outcome(result):
    if result.get('run_complete') or result.get('done'):
        return 'run_complete'
    if result.get('game_over'):
        return 'game_over'
    if result.get('level_completed'):
        return 'level_completed'
    return 'playing'


def compile_model(source):
    """A small, explicit API. Private attribute/name access is excluded."""
    tree = ast.parse(source, '<test1_model>')
    modules = {'math', 'collections', 'heapq', 'itertools', 'functools', 'copy', 'json', 'bisect'}
    forbidden = {'open', 'exec', 'eval', 'compile', 'globals', 'locals', 'vars', 'dir',
                 'getattr', 'setattr', 'delattr', 'input', 'breakpoint', 'help'}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'action':
            raise ValueError('real action calls are unavailable inside models')
        if isinstance(node, ast.Name) and (node.id.startswith('_') or node.id in forbidden):
            raise ValueError('model uses a prohibited name: ' + node.id)
        if isinstance(node, ast.Attribute) and node.attr.startswith('_'):
            raise ValueError('private model attributes are unavailable')
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [n.name for n in node.names] if isinstance(node, ast.Import) else [node.module or '']
            if getattr(node, 'level', 0) or any(n not in modules for n in names):
                raise ValueError('only pure model imports are supported')
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            raise ValueError('model state must be explicit')
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            raise ValueError('bare except is unavailable in executable models')
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name.startswith('_') and node.name != '__init__':
            raise ValueError('private model definitions are unavailable')
    safe_names = ('abs all any bool dict enumerate filter float frozenset int isinstance issubclass iter len list '
                  'map max min next pow range reversed round set slice sorted str sum tuple type zip '
                  'Exception ValueError TypeError KeyError IndexError AssertionError object property staticmethod').split()
    safe = {name: getattr(builtins, name) for name in safe_names}
    safe['__build_class__'] = builtins.__build_class__

    exports = {
        'collections': 'Counter defaultdict deque namedtuple OrderedDict ChainMap',
        'copy': 'copy deepcopy',
        'heapq': 'heapify heappop heappush heappushpop heapreplace merge nlargest nsmallest',
        'itertools': 'accumulate chain combinations combinations_with_replacement compress count cycle dropwhile filterfalse groupby islice pairwise permutations product repeat starmap takewhile tee zip_longest',
        'functools': 'cache lru_cache reduce partial cmp_to_key',
        'json': 'dumps loads',
        'bisect': 'bisect bisect_left bisect_right insort insort_left insort_right',
    }

    def model_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level or name not in modules:
            raise ImportError('model import unavailable')
        module = __import__(name, globals, locals, fromlist, level)
        names = [n for n in dir(module) if not n.startswith('_')] if name == 'math' else exports[name].split()
        # Avoid exposing implementation modules such as copy.sys through a
        # nominally pure import. Private function attributes are also AST-blocked.
        return types.SimpleNamespace(**{n: getattr(module, n) for n in names})

    safe['__import__'] = model_import
    namespace = {'__builtins__': safe, '__name__': 'test1_model'}
    exec(compile(tree, '<test1_model>', 'exec'), namespace, namespace)
    for name in ('State', 'init_state', 'transition', 'render', 'outcome'):
        if name not in namespace or not callable(namespace[name]):
            raise ValueError('missing callable model interface: ' + name)
    return namespace


class ModelTools:
    def __init__(self, rpc, get_state, real_action):
        self.rpc = rpc
        self.get_state = get_state
        self.real_action = real_action

    def transition_ids(self):
        return [transition_id(e['frame']) for e in self.get_state().get('history', []) if e.get('action')]

    def mechanics_put(self, id, rule, status='hypothesis', support_transition_ids=None,
                      counterexample_ids=None, applicability='', parameter_names=None):
        return self.rpc({'op': 'memory', 'record': {
            'id': id, 'rule': rule, 'status': status,
            'support_transition_ids': support_transition_ids or [],
            'counterexample_ids': counterexample_ids or [],
            'applicability': applicability, 'parameter_names': parameter_names or []}})

    def model_define(self, source):
        if not isinstance(source, str) or len(source.encode()) > 32768:
            raise ValueError('model source exceeds 32768 bytes')
        compile_model(source)  # Validate in child before committing source text on host.
        return self.rpc({'op': 'define', 'source': source})

    def _load(self):
        snapshot = self.rpc({'op': 'snapshot'})
        if not snapshot['model_enabled'] or not snapshot['source']:
            raise ValueError('define an executable model first')
        return snapshot, compile_model(snapshot['source'])

    @staticmethod
    def _prediction(model, state, frame, result=None):
        grid = compare_grid(model['render'](copy.deepcopy(state)), frame.get('grid', []))
        pred_outcome = model['outcome'](copy.deepcopy(state))
        if pred_outcome not in {None, 'unknown', 'playing', 'game_over', 'level_completed', 'run_complete'}:
            raise ValueError('outcome must be playing/game_over/level_completed/run_complete/unknown')
        known = pred_outcome not in {None, 'unknown'}
        expected = observed_outcome(result) if result is not None else None
        contradiction = grid['shape_error'] or grid['claimed'] != grid['correct'] or (
            expected is not None and known and pred_outcome != expected)
        return {**grid, 'outcome': pred_outcome, 'expected_outcome': expected,
                'outcome_claimed': int(expected is not None and known), 'contradiction': contradiction}

    def _replay(self, model):
        runtime = self.get_state()
        current = runtime.get('current_frame') or {}
        entries = runtime.get('history') or []
        entries = [e for e in entries if (e.get('frame') or {}).get('level') == current.get('level')]
        if not entries:
            raise ValueError('observed level history unavailable; use direct exploration')
        reports = []
        state = None
        previous_terminal = False
        previous_step = None
        for index, entry in enumerate(entries):
            frame = entry['frame']
            result = entry.get('result') or {}
            action_name = str(result.get('action_name') or entry.get('action') or '')
            anchor = index == 0 or action_name == 'RESET' or result.get('automatic') or previous_terminal
            # A current-level frame following a cleared previous level is a new anchor.
            if anchor:
                if index == 0 and entry.get('action') and action_name != 'RESET' and not result.get('automatic') and not result.get('level_completed'):
                    raise ValueError('initial level observation is missing; hidden state cannot be reconstructed')
                state = model['init_state'](copy.deepcopy(frame))
                report = self._prediction(model, state, frame)
                report['anchor'] = True
            else:
                if previous_step is not None and frame.get('step') != previous_step + 1:
                    raise ValueError('observation history has a gap; replay is unverified')
                action = {'action': entry.get('action'), 'data': result.get('action_data') or {}}
                # Use the public, model-facing action name with normalized coordinates.
                display = str(entry.get('action') or '')
                if '(' in display:
                    action['action'] = display.split('(', 1)[0].strip()
                action.update(action.pop('data'))
                state = model['transition'](copy.deepcopy(state), copy.deepcopy(action))
                report = self._prediction(model, state, frame, result)
                report['anchor'] = False
            report['transition_id'] = transition_id(frame)
            reports.append(report)
            # A completion result attached to the first frame of this new
            # level belongs to the preceding level. That frame is already the
            # new anchor; its following action is a genuine transition.
            previous_terminal = observed_outcome(result) != 'playing' and not (anchor and result.get('level_completed'))
            previous_step = frame.get('step')
        if binding(entries[-1]['frame'], '') != binding(current, ''):
            raise ValueError('current observation is not represented by recorded history')
        claimed = sum(r['claimed'] for r in reports)
        total = sum(r['total'] for r in reports)
        correct = sum(r['correct'] for r in reports)
        transitions = sum(not r['anchor'] for r in reports)
        outcome_claimed = sum(r['outcome_claimed'] for r in reports)
        contradictions = [r['transition_id'] for r in reports if r['contradiction']]
        coverage = claimed / total if total else 0.0
        accuracy = correct / claimed if claimed else None
        verified = not contradictions and coverage == 1 and transitions > 0 and outcome_claimed == transitions
        return state, {'status': 'contradicted' if contradictions else ('verified' if verified else 'unverified'),
                       'scope': 'observed current-level segments only', 'transitions': transitions,
                       'cell_accuracy': accuracy, 'prediction_coverage': coverage,
                       'outcome_coverage': outcome_claimed / transitions if transitions else 0.0,
                       'counterexample_ids': contradictions}

    def model_check(self):
        snapshot, model = self._load()
        _, report = self._replay(model)
        report['model_version'] = snapshot['version']
        self.rpc({'op': 'event', 'name': 'model_check', 'data': report})
        if report['status'] != 'verified':
            self.rpc({'op': 'plan', 'plan': None})
        return report

    @staticmethod
    def _usable(report, allow_partial):
        return report['status'] == 'verified' or (allow_partial and not report['counterexample_ids']
            and report['transitions'] > 0 and report['cell_accuracy'] == 1.0
            and report['prediction_coverage'] > 0 and report['outcome_coverage'] == 1.0)

    def model_plan(self, max_depth=32, max_states=50000, seconds=2.0, algorithm='bfs', allow_partial=False):
        seconds = float(seconds)
        if not math.isfinite(seconds):
            raise ValueError('seconds must be finite')
        seconds = max(.001, min(2.0, seconds))
        self.rpc({'op': 'plan', 'plan': None})
        snapshot, model = self._load()
        try:
            with _planner_budget(seconds):
                result = self._search_plan(snapshot, model, max_depth, max_states, seconds, algorithm, allow_partial)
        except _PlannerTimeout:
            result = {'status': 'time_limit', 'actions': []}
        # No IPC is performed while a signal timer is armed: interrupting recv()
        # could leave an old reply queued for the following request.
        plan = result.pop('_plan', None)
        self.rpc({'op': 'event', 'name': 'model_search', 'data': {k: v for k, v in result.items() if k != 'actions'}})
        if plan is not None:
            self.rpc({'op': 'plan', 'plan': plan})
        return result

    def _search_plan(self, snapshot, model, max_depth, max_states, seconds, algorithm, allow_partial):
        start, report = self._replay(model)
        if not self._usable(report, allow_partial):
            return {'status': 'unverified', 'validation': report, 'actions': []}
        if algorithm not in {'bfs', 'astar'}:
            raise ValueError('algorithm must be bfs or astar')
        if algorithm == 'astar' and not callable(model.get('heuristic')):
            raise ValueError('A* requires an explicit admissible heuristic')
        depth_cap = max(0, min(256, int(max_depth)))
        state_cap = max(1, min(50000, int(max_states)))
        seconds = float(seconds)
        if not math.isfinite(seconds):
            raise ValueError('seconds must be finite')
        deadline = time.monotonic() + max(0.001, min(2.0, seconds))
        frame = self.get_state()['current_frame']
        allowed = self.get_state().get('valid_actions') or []

        def key(s):
            value = model['state_key'](copy.deepcopy(s)) if callable(model.get('state_key')) else s
            return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

        def heuristic(s):
            h = float(model['heuristic'](copy.deepcopy(s))) if algorithm == 'astar' else 0.0
            if not math.isfinite(h) or h < 0:
                raise ValueError('heuristic must be finite and nonnegative')
            return h

        serial = 0
        queue = [(heuristic(start), serial, 0, start, [])]
        seen = {key(start): 0}
        expanded = 0
        found = None
        stop = 'exhausted'
        while queue:
            if time.monotonic() >= deadline:
                stop = 'time_limit'
                break
            _, _, depth, state, path = heapq.heappop(queue)
            if depth != seen.get(key(state)):
                continue
            outcome = model['outcome'](copy.deepcopy(state))
            if outcome in {'level_completed', 'run_complete'}:
                found = path
                stop = 'found'
                break
            if outcome == 'game_over' or depth >= depth_cap:
                continue
            if expanded >= state_cap:
                stop = 'state_limit'
                break
            expanded += 1
            actions = model['candidate_actions'](copy.deepcopy(state)) if callable(model.get('candidate_actions')) else [
                {'action': a} for a in allowed if a not in {'RESET', 'MOUSE'}]
            # Iterators can be infinite; count and time bounds apply while consuming.
            for n, action in enumerate(actions):
                if n >= 256 or time.monotonic() >= deadline:
                    break
                if not isinstance(action, dict) or action.get('action') not in allowed:
                    raise ValueError('candidate_actions must produce valid model-facing action dicts')
                if set(action) - {'action', 'row', 'col'}:
                    raise ValueError('candidate action has unsupported fields')
                if action['action'] == 'MOUSE' and any(type(action.get(k)) is not int for k in ('row', 'col')):
                    raise ValueError('MOUSE actions require integer row and col')
                if len(json.dumps(action)) > 512:
                    raise ValueError('candidate action exceeds bounds')
                # A generator may mutate and re-yield the same dict. Queue a
                # snapshot corresponding to the transition we actually simulated.
                action = copy.deepcopy(action)
                nxt = model['transition'](copy.deepcopy(state), copy.deepcopy(action))
                k = key(nxt)
                if seen.get(k, depth + 2) <= depth + 1:
                    continue
                if len(seen) >= state_cap:
                    stop = 'state_limit'
                    continue
                seen[k] = depth + 1
                serial += 1
                heapq.heappush(queue, (depth + 1 + heuristic(nxt), serial, depth + 1, nxt, path + [action]))
        result = {'status': stop, 'algorithm': algorithm, 'expanded': expanded, 'discovered': len(seen),
                  'actions': found or [], 'validation': report,
                  'optimality': 'unit-cost BFS' if algorithm == 'bfs' else 'conditional on heuristic admissibility'}
        if found:
            result['_plan'] = {'binding': binding(frame, snapshot['version']), 'actions': found,
                               'allow_partial': bool(allow_partial)}
        return result

    def model_act(self, max_actions=16):
        snapshot, model = self._load()
        plan = snapshot.get('plan')
        frame = self.get_state()['current_frame']
        if not plan or plan.get('binding') != binding(frame, snapshot['version']):
            self.rpc({'op': 'plan', 'plan': None})
            self.rpc({'op': 'event', 'name': 'stale_plan'})
            return {'status': 'stale_plan', 'executed': 0}
        state, report = self._replay(model)
        if not self._usable(report, plan.get('allow_partial', False)):
            self.rpc({'op': 'plan', 'plan': None})
            return {'status': 'unverified', 'executed': 0, 'validation': report}
        actions = plan['actions']
        executed = 0
        # Consume the host plan BEFORE executing; timeout/refusal cannot replay it.
        self.rpc({'op': 'plan', 'plan': None})
        for index, action in enumerate(actions[:max(0, min(256, int(max_actions)))]):
            before = self.get_state()['current_frame']
            predicted = model['transition'](copy.deepcopy(state), copy.deepcopy(action))
            real = self.real_action([copy.deepcopy(action)])
            if not real.get('executed'):
                return {'status': 'refused', 'executed': executed}
            executed += 1
            frame = self.get_state()['current_frame']
            check = self._prediction(model, predicted, frame, real)
            if frame.get('level') != before.get('level') and observed_outcome(real) in {'level_completed', 'run_complete'}:
                # The environment may already display the next unseen layout.
                # Score the terminal prediction, not unknowable next-level pixels.
                check.update(claimed=0, correct=0, total=0, shape_error=False, boundary_frame_unscored=True,
                             contradiction=check['outcome'] not in {None, 'unknown', observed_outcome(real)})
            self.rpc({'op': 'event', 'name': 'prediction', 'data': check})
            terminal = observed_outcome(real) != 'playing'
            if check['contradiction']:
                self.rpc({'op': 'event', 'name': 'contradiction', 'data': {
                    'transition_id': transition_id(frame), 'model_version': snapshot['version'], 'check': check}})
                return {'status': 'contradiction', 'executed': executed, 'counterexample_id': transition_id(frame)}
            if terminal:
                return {'status': 'terminal', 'executed': executed, 'outcome': observed_outcome(real)}
            if check['claimed'] == 0 or (check['claimed'] != check['total'] and not plan.get('allow_partial')) or check['outcome'] in {None, 'unknown'}:
                return {'status': 'unverified_prediction', 'executed': executed}
            state = predicted
        remaining = actions[executed:]
        if remaining:
            self.rpc({'op': 'plan', 'plan': {'binding': binding(frame, snapshot['version']), 'actions': remaining,
                                           'allow_partial': plan.get('allow_partial', False)}})
        return {'status': 'paused' if remaining else 'complete', 'executed': executed, 'remaining': len(remaining)}
