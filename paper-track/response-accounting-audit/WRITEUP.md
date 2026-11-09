# Auditing Token Accounting and Tool Dispatch in an ARC-AGI-3 Agent

*Response-to-action accounting, capped programs, and limits of feature comparisons*

**Jiayi Zhang** | University of California, Berkeley

## Abstract

I audit development runs of one system (linked submission 57684318), alongside native baseline evidence, through token partitioning, capped-call replay and feature-exposure checks. Across five populations, action-issuing responses carry approximately 46-57% of completed generation and the terminal suffix 2.6-7.9%. The partition reconciles usage; native action history alone omits its suffix. In three pre-guard arms, capped replies consume 6-8% of generation. Of 26,484 responses, 29 expose capped Python payloads; eight parse and one issues an action. Feature comparisons remain inconclusive; score gains are not established.

## Submitted system

ARC-AGI-3 agents infer unfamiliar games' rules from observations and actions. Scores combine level completion with action efficiency relative to humans; later levels receive more weight [1]. The inherited Duck/Franzen harness [2,3] lets a model inspect boards and run Python in a persistent REPL. Python may analyze observations or issue game actions. Reasoning consumes compute without necessarily spending actions.

| Linked submission: guarded Test1 R2 | Configuration |
|---|---|
| Identity | Submission **57684318**, exact notebook V1; public score **20.02** |
| Model/serving | Qwen3.8-Flash-Next W4A16; Pennyroyal SGLang; MTP decoding [3,4] |
| Sampling/resources | Temperature 0.7; ten admitted streams; RTX Pro 6000; nine-hour ceiling |
| Capacity | 131,072 harness / 139,264 server tokens; 12,288 reply allowance |
| Test1 additions | Context/usage checks, bounded lifecycle, executable-model tools, capped-call guard; mechanics memory off |

R0 is the hardened control; R1 adds mechanics memory, R2 executable-model tools, and planned R3 both. The R0-R2 comparison predates the guard and does not measure its performance. Model tools support simulators and planning; direct actions remain available.

Separate native Franzen/Fang reproductions scored 26.39/26.31, versus historical author-page values 33.68/33.94. Guarded R2 scored lower, but these unmatched runs do not identify a causal effect.

## Related work

*AI Agents That Matter* motivates cost control [8]. HAL's Appendix A4.1 reports charging full SWE-Agent token prices despite cache hits [9]. ReAct, Reflexion and Fang precede the reasoning/memory ideas [5-7]. This contribution is a narrower accounting and dispatch audit.

## Audit and rationale

**Capped** means finish reason `length` at the observed 12,288-token allowance. **Charging** adds returned completion usage to a counter; it is not dollar billing. The **terminal suffix** is generation after the episode's last action. Unanswered requests remain unknown.

Align transcript metadata and usage events by game/pass and response order, checking counts/finish reasons; use Test1 token traces or native game-named logs. Match action history by game/pass. Under atomic pre-dispatch charging, exact cumulative usage boundaries identify action-issuing responses; intervening replies did not issue actions, and the remaining suffix is terminal. This is accounting attribution, not useful-reasoning measurement. Reserve the full reply against context capacity and preserve valid user/tool history when trimming.

A generation cap can end at a statement boundary, leaving a parseable prefix. Executing it can spend actions before an intended continuation exists; extra actions penalize a completed level approximately as the inverse square of action count [1]. The guard rejects all cap-flagged calls before dispatch/history insertion, preserves recoverable reasoning, and stops after four consecutive malformed or capped-call replies. It may reject actually complete code; that cost is unmeasured.

## Response and dispatch evidence

Shares are **percentages of completed generation**, not response counts. Terminal takes precedence; cap status overlaps the partition. Other-tool/no-call work is not necessarily waste.

| Population | Tokens | Action | Other tool | No call | Terminal |
|---|---:|---:|---:|---:|---:|
| R0 | 17,674,210 | 45.73 | 45.07 | 5.92 | 3.28 |
| R1 | 17,048,235 | 48.72 | 42.76 | 5.90 | 2.62 |
| R2 | 17,169,163 | 45.92 | 45.78 | 4.90 | 3.41 |
| Guard qualification | 937,189 | 57.12 | 27.11 | 7.87 | 7.90 |
| Native Franzen | 903,752 | 46.52 | 47.38 | 1.36 | 4.74 |

R0-R2 each cover 100 public episodes under a nine-hour notebook ceiling; qualification has 20 responding episodes and five unadmitted games under one hour. Native practice covers ten games with 25-minute budgets. Workloads differ; duration effects are unidentified. Unanswered requests number 7/8/18/20/5 respectively; these totals exclude unknown work.

Native action history omits 42,811 completed tokens; solver cumulative counters retain them. Completed generation is 595.24 tokens/s over a shared 1,518.31-second gameplay interval, excluding startup. Server billing remains unresolved. Qualification's maximum prompt plus full reply is 130,446, leaving 626 tokens; an 11-token estimation shortfall fit the reserve.

The 11-token shortfall occurs in all 8,840 completed R0 requests. A post-hoc serializer candidate eliminates it on 145 sampled requests; the scored estimator remains unchanged.

| Pre-guard arm | Capped tool replies | Invalid / parseable / empty | Actions | All-cap token share |
|---|---:|---|---:|---:|
| R0 | 12 | 9 / 2 / 1 | 0 | 8.00% |
| R1 | 8 | 4 / 4 / 0 | 1 | 6.78% |
| R2 | 9 | 7 / 2 / 0 | 0 | 6.16% |

The 29 payloads consumed 356,352 tokens; all 295 capped replies consumed 3,624,960. These are exposure costs, not measured harm. One parseable R1 call produced a recorded mouse action, corroborated by its tool result; its utility is unknown. Parseability does not certify completeness. Earlier private mocked replay blocked all 29 payloads, retaining charges and testing continuation without executing saved game code. Qualification recovery used fixtures, with no naturally capped tool payload.

## Feature comparisons and limitations

Across 25 public games and four episodes per arm, both completed comparisons are reported:

| Arm | Mean score | Difference from R0 | Adjusted bootstrap interval |
|---|---:|---:|---|
| R0 | 44.71 | - | - |
| R1 | 45.54 | +0.83 | [-6.85, +8.21] |
| R2 | 49.12 | +4.41 | [-3.23, +11.78] |

The paired-game bootstrap uses 12,000 draws, seed 20261024 and alpha=0.05/3 for three planned comparisons; R3 was not run. Neither interval excludes zero. Zero observed model-API calls rules out evidence of that intended mechanism, not prompt-mediated effects from exposing the tools.

A separate verbatim-note screen uses five games, two paired blocks, five streams per arm sharing a server, and reversed launch order. Notes-off/on means are 35.36/32.17; 13 nonempty flushes expose notes in eight treatment episodes. Differences use unrounded values. Within-condition scores differ: ar25 notes-on 77.78 versus 58.33 (19.44 points), lp85 notes-off 21.42 versus 41.67 (20.25). These exceed the overall 3.20-point arm difference but not the largest paired gap, 41.67. Two blocks, shared serving and reused games do not establish a general memory effect.

**Figure 1.** Each connected pair is one game/block, notes off versus on. All 20 episode scores are shown; overlapping equal scores are indicated. These are descriptive observations, not independent game-level replications.

In a separate CPU fixture, four consecutive capped 512-token replies expose another limitation: the submitted guard charges all 2,048 tokens but returns third-reply reasoning instead of fourth-reply reasoning. A separate post-hoc repair has CPU tests, but no neural performance result. Submitted source is unchanged.

## Conclusion

Cap-flagged dispatch issued one action in 26,484 responses: rare, with unknown score impact. Capped replies' 6-8% generation share is measured exposure, not proven waste. Transfer requires ordered usage/finish records and compatible action accounting; dispatch checks also require payloads. Applicability is untested beyond this system. Reused development games, unavailable hidden traces and no isolated guard ablation preclude score-gain or generalization claims.

## Availability

The [public package](https://github.com/laurence5kg/arc-agi-3-checkpoint-1/releases/tag/paper-audit-v1-20261108), tag `paper-audit-v1-20261108`, was released November 9, 2026. Evidence-manifest SHA-256: `96c896a46f880119afd8cae611da5ce7ca043122ec0cff2adf04bc357414c197`. Original code contributions are MIT-0; the paper is CC-BY 4.0. Upstream licenses remain applicable. The linked public artifact is [R2 V1](https://www.kaggle.com/code/laurencezhang10kg/arc-agi3-test1-r2-probe-20261026?scriptVersionId=362655599), submission 57684318. Scalar records identify population, episode, response ordinal, completion tokens, class and cap flag, enabling partition recomputation. Full finish reasons, raw logs and saved Python payloads remain private, limiting independent source verification and replay.

## References

[1] ARC Prize. [Scoring methodology](https://docs.arcprize.org/methodology).

[2] Tufa Labs. [Duck](https://github.com/Tufalabs/duck-harness).

[3] Daniel Franzen. [Milestone 2 solution](https://github.com/da-fr/arc-agi-3-solution).

[4] Zheng et al. [SGLang](https://arxiv.org/abs/2312.07104); Pezzulli. [Pennyroyal](https://github.com/jpezzulli/sglang-rtxpro6000).

[5] Yao et al. [ReAct](https://arxiv.org/abs/2210.03629).

[6] Shinn et al. [Reflexion](https://arxiv.org/abs/2303.11366).

[7] Yiming Fang. [Lalalia V1](https://www.kaggle.com/code/vickyfym/arc-agi-3-lalalia-final).

[8] Kapoor et al. [AI Agents That Matter](https://arxiv.org/abs/2407.01502).

[9] Kapoor et al. [Holistic Agent Leaderboard](https://arxiv.org/abs/2510.11977).
