"""Host-side data only: no model source is executed in this process."""
from __future__ import annotations

import hashlib
import copy
import json
import os
from pathlib import Path


def enabled(name):
    return os.environ.get('TEST1_' + name, '0') == '1'


def guidance():
    lines = []
    if enabled('MEMORY'):
        lines.append('Optional mechanics memory: mechanics_put(id, rule, status="hypothesis", '
                     'support_transition_ids=[], counterexample_ids=[], applicability="", parameter_names=[]). '
                     'Use transition_ids() to get observed evidence IDs. Status may be observation, hypothesis, '
                     'contradicted, or superseded. This is your fallible notebook, not an oracle; refresh layout parameters.')
    if enabled('MODEL'):
        lines.append('Optional executable-model tools inside python: model_define(source), model_check(), '
                     'model_plan(max_depth=32, max_states=50000, seconds=2.0, algorithm="bfs"), model_act(max_actions=16). '
                     'Source defines State (a class or alias), init_state(observation), transition(state, action), '
                     'render(state) returning a 2D grid (ARC color letters or IDs 0..15; None cells mean unknown), outcome(state) returning '
                     'playing/game_over/level_completed/run_complete or unknown. Observation has grid, step, level. '
                     'Actions are dicts such as {"action":"RIGHT"} or {"action":"MOUSE","row":4,"col":3}; '
                     'candidate_actions(state), state_key(state), heuristic(state) are optional. '
                     'Within model observations, grid IDs follow WwgGcBMPRbSYOrNp at indexes 0..15; ascii is also supplied. '
                     'Keep these functions pure; only safe standard library imports are available. '
                     'init_state starts at the observed reset/level boundary and history is replayed to recover hidden state. '
                     'Check reports coverage separately from accuracy; partial or untested models are unverified. '
                     'Planning requires consistent evidence; full coverage is default. Explicit allow_partial=True permits '
                     'a consistent model with positive coverage and known outcomes, and keeps it labeled unverified. '
                     'A* also requires heuristic(state), assumed admissible by you. '
                     'model_act executes one real action at a time through action(), stopping at any disagreement or terminal boundary. '
                     'Direct exploratory action() remains available without a model. Never spend a long time modeling before acting.')
    return '\n\nTEST1 OPTIONAL TOOLS\n' + '\n'.join(lines) if lines else ''


class FeatureSession:
    """One per game. Mutations survive a sandbox exception or timeout."""
    def __init__(self, *, memory=None, model=None, log_path=None):
        self.memory_enabled = enabled('MEMORY') if memory is None else memory
        self.model_enabled = enabled('MODEL') if model is None else model
        self.memory = {}
        self.revision = 0
        self.source = ''
        self.version = ''
        self.plan = None
        self.evidence_ids = set()
        self.level = None
        self.last_capsule = None
        self.log_path = Path(log_path) if log_path else None
        self.metrics = {}

    @property
    def active(self):
        return self.memory_enabled or self.model_enabled

    def sync(self, state):
        frame = state.get('current_frame') or {}
        self.level = frame.get('level')
        # Stable IDs use the actual action counter and level, never an LLM label.
        for entry in state.get('history') or []:
            f = entry.get('frame') or {}
            if entry.get('action') and (entry.get('result') or {}).get('executed', True):
                self.evidence_ids.add(f"L{f.get('level')}:A{f.get('step')}")

    def event(self, name, data=None):
        self.metrics[name] = self.metrics.get(name, 0) + 1
        if self.log_path:
            try:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open('a', encoding='utf-8') as f:
                    f.write(json.dumps({'event': name, 'data': data}, ensure_ascii=True) + '\n')
            except OSError:
                # Optional diagnostics never suppress gameplay or replay an action.
                pass

    def request(self, request):
        if not self.active:
            raise ValueError('test1 features disabled')
        if len(json.dumps(request, ensure_ascii=True)) > 100_000:
            raise ValueError('test1 request too large')
        op = request.get('op')
        if op == 'snapshot':
            return {'memory_enabled': self.memory_enabled, 'model_enabled': self.model_enabled,
                    'source': self.source, 'version': self.version, 'plan': self.plan}
        if op == 'memory':
            if not self.memory_enabled:
                raise ValueError('mechanics memory disabled')
            record = copy.deepcopy(dict(request.get('record') or {}))
            allowed = {'id', 'rule', 'status', 'support_transition_ids', 'counterexample_ids',
                       'applicability', 'parameter_names'}
            if set(record) - allowed:
                raise ValueError('unknown memory fields')
            key = record.get('id')
            if not isinstance(key, str) or not 1 <= len(key) <= 64:
                raise ValueError('id must be 1..64 characters')
            if not isinstance(record.get('rule'), str) or not record['rule'].strip():
                raise ValueError('rule must be nonempty text')
            if record.get('status') not in {'observation', 'hypothesis', 'contradicted', 'superseded'}:
                raise ValueError('invalid evidence status')
            for field in ('support_transition_ids', 'counterexample_ids'):
                ids = record.get(field, [])
                if not isinstance(ids, list) or any(not isinstance(i, str) or i not in self.evidence_ids for i in ids):
                    raise ValueError('evidence ID was not observed in this game')
                record[field] = list(dict.fromkeys(ids))
            if record['status'] == 'observation' and not record['support_transition_ids']:
                raise ValueError('an observation needs recorded support')
            if record['status'] == 'contradicted' and not record['counterexample_ids']:
                raise ValueError('contradicted rules need a recorded counterexample')
            if record['counterexample_ids'] and record['status'] not in {'contradicted', 'superseded'}:
                raise ValueError('counterexamples require contradicted or superseded status')
            if not isinstance(record.get('applicability', ''), str):
                raise ValueError('applicability must be text')
            params = record.get('parameter_names', [])
            if not isinstance(params, list) or any(not isinstance(p, str) for p in params):
                raise ValueError('parameter_names must be text names')
            updated = dict(self.memory)
            updated[key] = record
            # UTF-8 byte / 4 is an explicit estimate, not a tokenizer measurement.
            if len(json.dumps(updated, ensure_ascii=False).encode('utf-8')) > 4000:
                raise ValueError('mechanics memory cap reached (~1000 estimated tokens); revise/supersede shorter records')
            self.memory = updated
            self.revision += 1
            self.event('memory_update', {'id': key, 'status': record['status']})
            return copy.deepcopy(record)
        if not self.model_enabled:
            raise ValueError('executable model disabled')
        if op == 'define':
            source = request.get('source')
            if not isinstance(source, str) or not 1 <= len(source.encode('utf-8')) <= 32768:
                raise ValueError('model source must be 1..32768 bytes')
            self.source = source
            self.version = hashlib.sha256(source.encode('utf-8')).hexdigest()
            self.plan = None
            self.event('model_define', {'version': self.version})
            return {'version': self.version}
        if op == 'plan':
            plan = request.get('plan')
            if plan is not None and (not isinstance(plan, dict) or len(plan.get('actions', [])) > 256
                                     or len(json.dumps(plan)) > 65536):
                raise ValueError('plan exceeds bounds')
            self.plan = copy.deepcopy(plan)
            return {'stored': plan is not None}
        if op == 'event':
            name = request.get('name')
            if name not in {'model_check', 'model_search', 'prediction', 'contradiction', 'stale_plan'}:
                raise ValueError('unknown event')
            self.event(name, request.get('data'))
            return {'recorded': True}
        raise ValueError('unknown test1 operation')

    def capsule(self, *, force=False):
        marker = (self.revision, self.level)
        if not self.memory_enabled or not self.memory or (not force and marker == self.last_capsule):
            return ''
        self.last_capsule = marker
        return '\n\nMECHANICS MEMORY (fallible; hypotheses are unverified; refresh layout parameters):\n' + json.dumps(
            list(self.memory.values()), ensure_ascii=False, separators=(',', ':'))
