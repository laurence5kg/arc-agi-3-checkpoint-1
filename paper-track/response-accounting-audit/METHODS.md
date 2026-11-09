# Methods and reproducibility appendix

This is supporting material for the short Kaggle Writeup. It does not replace required submission fields or extend the Writeup word allowance. See LICENSE.md for the approved scope of licensing.

## Submission identity and terminology

The method entry is guarded Test1 R2, scored submission **57684318**, notebook Version 1 of `laurencezhang10kg/arc-agi3-test1-r2-probe-20261026` (script version 362655599), public score 20.02. The exact committed notebook is the deployment source. This replay subset is not a replacement notebook.

R0 is the inherited Franzen/Duck agent with Test1 context, usage and lifecycle changes, with mechanics memory and executable-model additions disabled. R1 enables mechanics memory; R2 enables executable-model tools; R3 would enable both. R0-R2 benchmark data were collected before the output guard. The later guarded R2 qualification and scored submission have a different frozen source identity. The retention A/B is another separate candidate, with verbatim reasoning notes rather than R1's mechanics records or Fang's solved-level memory.

| Evidence | Identity / population | Scope |
|---|---|---|
| Pre-guard R0/R1/R2 | Source-manifest SHA-256 `3a12a0949b8bcbfa1e498fd23dea08c79a01f32b67cda82d8e4e9eeff75f2f33`; 25 games x four episodes x three arms | Public reused development games; 300 episodes |
| Guarded R2 | Source-manifest SHA-256 `4b7dfe1e7a46d9166deca16831c89d739f36f34434b650527d24700859f7f46f` | One-hour qualification, then separately scored ID 57684318 |
| Native Franzen | Exact native V1; ten public games; separate scored ID 57887968 | Practice throughput/accounting; scored result 26.39 is a separate population |
| Native Fang | Exact native V1; separately scored result 26.31 | Attributed reproduction; not a guard experiment |
| V83-derived | Roman Tamrazov version 83, with reviewed deployment/startup changes | Separate scored result 27.45; not a native copy or guard result |
| Post-hoc tests | November 4 and November 6 local CPU probes | Replays and a separately labeled terminal-reasoning repair; no new neural gameplay |

The linked R2 uses Qwen3.8-Flash-Next W4A16, the reference MTP draft, Pennyroyal v2.5.3 plus inherited patches, ten admitted streams and ten server requests, temperature 0.7, top-p 0.95, top-k 20, a 131,072-token harness window, 139,264-token server window, 12,288 reply tokens and a 512-token request reserve. Board upscale is 10. These values come from the frozen build and returned committed notebook, rather than the earlier exploratory Milestone 2 configurations described in conversation. The model was not trained in this project.

Mechanics memory stores bounded game-local records with evidence and status. Executable-model tools expose `model_define`, `model_check`, `model_plan` and `model_act`: propose a simulator, check observed transitions, search a bounded plan, and interrupt on contradiction. They are optional; the ordinary Python/action route remains available. Test1 also checks full-context requests, reconciles completed generation and bounds deadline/retry/cleanup paths. The guard extends the inherited malformed-JSON handling to every cap-flagged tool response, including valid JSON/Python. No invention claim is made for the inherited harness, serving stack or memory idea.

## Token partition: assumptions and reconstruction

For each episode, let completed response usage be the ordered positive sequence g. The solver charges returned usage atomically before tool dispatch. Each positive `history.generated_tokens` entry equals generation since the preceding accepted action. Starting at the previous response boundary, sum g until that charge is reached exactly. The last included response is action-issuing; all preceding responses in that interval are not. Subsequent zero-charge actions belong to the same response. An initial zero-charge automatic RESET is counted separately. Noninitial zero-charge actions without an owner, partial-response charges, missing responses and zero-token response ambiguity cause the extractor to fail rather than guess.

The remaining response suffix after the last action is terminal. Earlier responses are divided into action-issuing, visible tool-call without an action, and no visible call. Terminal takes precedence so these four categories are disjoint. A cap flag is independent and overlaps any category. A `non_action_tool` category includes analysis, helper definitions, errors and other tool work; it is not a semantic claim that all such work was useful. Likewise, a no-call response can contain reasoning that helps a later action. A response classified action-issuing can contain extensive reasoning and several actions; all of its completion tokens are assigned to that category, not split by token purpose.

Exact token-boundary matching succeeds for every episode with returned generation in the five populations. Per-response counts, tokens, categories, cap flags and attributed action counts are included in `data/response_audit.json`. For R0/R1/R2 and qualification, response order and usage come from token traces matched to transcript metadata. Native Franzen uses the separate game-named request logs, streamed without making a global join on repeating action/index tuples. Native transcript order matches response records. Source transcript and usage-log hashes are retained. Only aggregate/per-response scalar records are staged. Raw boards, request logs and saved generated Python are private; generated payloads can contain board-specific constants.

The interpretation of action ownership relies on the inspected charge-before-dispatch contract, not solely on coincidentally matching integers. Tool-result `[action]` strings are not authoritative for counting, because model code can print arbitrary strings. The single capped response with a recorded action is independently corroborated by its mouse tool result. No saved model Python is executed during extraction or replay.

Conservation holds as `completed generation = action-history generation + terminal generation`. This is a completed-client-response partition, not a total server bill. In Test1 the final-turn field already reports the suffix. In native Franzen the cumulative solver counters retain it while action history omits it. It would be incorrect to say all implementations lost the terminal tokens internally.

| Population | Responses | Action-issuing / other-tool / no-call / terminal counts | Terminal tokens | Unanswered requests |
|---|---:|---|---:|---:|
| R0 | 8,840 | 4,191 / 4,400 / 87 / 162 | 579,806 | 7 |
| R1 | 8,740 | 4,213 / 4,278 / 86 / 163 | 446,345 | 8 |
| R2 | 8,904 | 4,171 / 4,493 / 70 / 170 | 584,738 | 18 |
| Qualification | 582 | 327 / 222 / 6 / 27 | 74,065 | 20 |
| Native Franzen | 580 | 270 / 285 / 1 / 24 | 42,811 | 5 |

Qualification declares 25 games: five were never admitted and have no requests, generation or actions. They stay in the declared denominator; the 20 responding episodes define the response partition. Initial automatic resets contribute no response tokens and are excluded from the response-owned action totals, not from official score accounting. R0/R1/R2 each have a nine-hour whole-notebook ceiling, not nine hours per game. Qualification has a one-hour whole-notebook ceiling; native gameplay uses 25-minute per-game budgets. Startup, allocation, game mix and stopping differ, so the duration contrast does not identify a scaling law.

Native common-wall throughput is 903,752 / 1,518.310479 = 595.2353 completed generation tokens/s. It excludes startup. Five requests lack completion usage, and server populations cannot all be matched unambiguously. Neither full compute billing nor hidden-rerun throughput is established. Decode-log quantiles are not time-weighted utilization.

## Capped responses and dispatch

Across R0-R2, 295 length finishes consume 3,624,960 tokens. Twenty-nine expose Python tool payloads: 20 invalid Python, eight parseable Python and one missing-code payload. Their 356,352 tokens are a subset of the all-cap total, not an additional cost. One parseable R1 response issued one mouse action; neither its usefulness nor its harm is identified. The cap flag does not prove that code was semantically incomplete. Discarding all cap-flagged calls is conservative and may block complete valid code.

These are transcript-visible calls after the harness's existing markup recovery and malformed-argument filtering. They are not a census of every tool call the model may have attempted before filtering. A no-visible-call category can include an attempted malformed call. The cap flag and token counts come independently from the completed-response usage log.

The context-free code-tail listing was removed from the manuscript. The original R2-cap-09 payload ends `return T` followed by `T=grid`, and its full Python parses. No omitted continuation or intended target is inferred. Original selected calls are private. `data/capped_case_metadata.json` retains their scalar metadata and prior classifications without code; independent AST inspection requires the private payloads. Metadata-display shortening was recovered from separate complete dispatch blocks for 42/43/29 R0/R1/R2 responses; this is not proof of model-context truncation.

`replay_saved_caps.py` feeds all 29 calls to the actual byte-verified frozen guard, with a synthetic recoverable reasoning string and a second seven-token recovery response. It asserts the old calls cannot dispatch or re-enter continuation history, while the synthetic recovery marker can. Network and saved-code execution are prohibited. These are tests of dispatch and accounting behavior, not counterfactual gameplay. The original qualification had six cap finishes but zero naturally capped tool payloads; forced fixtures supplied its recovery evidence.

## Post-hoc terminal repair

The original four-cap probe still returns `CAP_REASONING_3` after replies 1-4 and retains all 2,048 completion tokens. `posthoc_terminal_reasoning.patch` adds capture of the latest nonempty reasoning just before the terminal four-failure exception. It preserves the same stop rule, charges and zero dispatches. This is a repair to returned terminal reasoning, not a guarantee of future-history persistence after terminal failure.

`check_terminal_repair.py` verifies the frozen source hash, copies the runtime into a temporary directory, applies exactly that change and starts isolated CPU processes. Six cases compare original and repaired behavior for four capped calls, four malformed-JSON calls, and an empty fourth reasoning field. The repaired version returns reply four when nonempty and reply three when reply four is empty. The frozen runtime remains byte-identical. No modified notebook or scored result is produced; neural effects remain unmeasured.

## Feature screens and statistical limits

The five retention games (ar25, bp35, lp85, re86, sk48) run in two paired blocks with five streams per arm sharing one server; launch order reverses. Figure 1 shows each episode, not game means. Two episode pairs per game are not independent game replications. Notes are inserted on 13 nonempty flushes in eight treatment episodes. Their insertion does not establish model use or correctness. The arm mean difference is -3.19518, including ar25 -31.94444 and lp85 +18.45796; no general memory harm is inferred.

R0/R1/R2 each average four episodes for each of 25 games. All completed baseline comparisons are reported: R1-R0 +0.83177 with interval [-6.85463, 8.21409], R2-R0 +4.40878 with interval [-3.23087, 11.78177]. The pre-existing evaluation plan includes three comparisons (R1/R2/R3 versus R0); alpha=0.05/3 is retained although R3 was not run. The standard-library script reproduces 12,000 paired-game bootstrap draws with `random.Random(20261024)` and the original integer-index percentile rule. This adjustment does not guarantee nominal coverage on reused development games. The exploratory R2-R1 comparison is not a third planned baseline comparison and is not used to claim promotion. Zero observed model API calls does not rule out prompt effects of advertising tools.

Historical author-page screenshots show Franzen public 33.68 and best 34.30 V1, Fang 33.94 V1, and Roman's current 29.01 versus best 35.35 V83. Fang's narrative also mentions 31.46; that inconsistency is retained as unresolved, not converted into an estimated variance. My scored results and author snapshots are unmatched executions, with no evidence of equal delivered compute or identical hidden traces. No run-to-run standard deviation is estimated from them.

## Relation to prior work

HAL (Kapoor et al., arXiv:2510.11977, sections 2-3 and Appendix A4.1) provides shared evaluation infrastructure and log analysis. It identifies incomplete cache-aware cost accounting for SWE-Agent. This paper's gap is different: generation after the last environment action can be absent from an action-keyed export even when cumulative solver counters include it. AI Agents That Matter (Kapoor et al., arXiv:2407.01502, sections 2 and 6) motivates cost control and documents reproducibility failures. The contribution here is an auditable case study and executable counterexamples, not the discovery that evaluation needs cost accounting. ReAct, Reflexion, SGLang and Fang's notebook remain credited. Fang's full writeup was unavailable, so overlap cannot be exhaustively assessed.

## Reproduction and publication scope

Run `python analyze.py` for the aggregate results and bootstrap intervals, and `python analyze_public_scalars.py` for the five response populations and all 8,840 saved R0 estimator pairs. `data/response_audit.json` stores population, episode (`run`), response ordinal, completion tokens, category, cap flag and counts; it does not store full finish-reason strings. Scalar regrouping reproduces the token partition, but does not independently prove raw-log alignment.

`python render_figures.py` rebuilds the figures. The synthetic terminal probe and repair tests remain runnable with their pinned dependencies. Original `analyze_responses.py` and `replay_saved_caps.py` are retained for provenance but require the privately held `data/pooled_capped_responses.json`; they cannot reproduce the 29 original payload cases from this public subset. No raw boards, requests, transcripts or saved generated programs are distributed.

All 42 runtime files remain unchanged and are identified by `runtime_manifest.json`. The current public-subset evidence manifest has a new hash; it references the earlier private manifest hash as provenance, not as an assertion that the public subset contains every earlier file. Newly published scalar projections are distinguishable from older diagnostic results. No new neural run or score is claimed.

Jiayi Zhang, University of California, Berkeley, is the sole author. AI assistance was used for code, analysis and drafting; the author must review and take responsibility for the final claims. Original contributions are licensed as described in LICENSE.md; upstream notices are retained. The exact scored notebook is public. Author/account metadata and private review files are excluded from the release archive.

## Text-revision clarifications - November 7

Charging is accumulation of returned completion usage, not currency billing. The terminal suffix is all completed responses after the final action in an episode. Every observed `length` finish in these five populations reports the 12,288-token reply allowance. The terms describe this dataset and are not assumed to cover every provider's finish semantics.

Alignment uses game/pass identity and within-file response order, verifies counts and finish reasons, and then reconstructs exact cumulative token boundaries against action history. It does not join on repeated native action/within-turn indices. Transfer beyond this system is untested and requires compatible atomic charging and recoverable ordering; usage, finish reason and an arbitrary action log alone do not guarantee identification.

The saved post-hoc serializer candidate (145 requests from two R0 logs) reproduces `function.strict=false` and `tool.defer_loading=null` under the pinned server's tool models. Original estimates are 11 tokens low in all 145 rows; normalized estimates equal returned usage in all rows. `data/serving_token_normalization_proof.json` preserves the prior diagnostic, hashes and scope limitations. This revision checks its rows but does not rerun model inference or claim a correction in the scored estimator. Raw request payloads are not distributed, limiting independent mechanistic replication from the archive alone.

Within-condition retention differences are ar25 notes-on 77.77778 versus 58.33333 (19.44444 points) and lp85 notes-off 21.41741 versus 41.66667 (20.24925). The largest absolute paired treatment difference is 41.66667; the within-condition spreads are smaller, though both exceed the approximately 3.20-point overall arm difference. These examples are not estimates of a population variance.

One cap-flagged response issued an action among 26,484 pre-guard responses (about 0.0038%). Its score effect is unknown. Rarity does not bound harm, and the 6-8% capped-generation share is not automatically wasted compute.

The code/evidence manifest excludes prose so that its digest can appear in the paper without a circular hash. The full archive has a separate manifest. The public MIT-licensed September checkpoint (laurence5kg/arc-agi-3-checkpoint-1, commit 8640681f348eb3163dc315d291fa1a51d1e101fa) has no current audit package. The current release publishes the reviewed scalar/code subset under the licenses described in LICENSE.md; its public availability is identified in the paper.
