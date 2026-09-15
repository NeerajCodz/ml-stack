# ML-Stack — Product & Architecture Specification

**Portable autonomous ML research, experimentation, challenge-solving, benchmarking, and model-development plugin suite**

- **Project name:** ML-Stack
- **Repository name:** `ml-stack`
- **Primary invocation:** `/ml-stack`
- **Specification status:** v1.0 / comprehensive end-to-end architecture and implementation lock
- **Date:** 2026-09-14
- **Primary design references:** Hugging Face `huggingface/ml-intern` and Garry Tan's `garrytan/gstack`
- **ML Intern parity snapshot:** `huggingface/ml-intern` at commit `b0d6752723d17ef2ea7a54f5aeb63abebba99e47`
- **Design rule:** ML-Stack must be a **plugin/tool layer**, not a separate chatbot or mandatory user interface.

> **Naming lock:** The product, repository, command family, Skill namespace, and portable capability pack are named **ML-Stack / `ml-stack`**. The canonical slash command is **`/ml-stack`**. The optional remote daemon is **`ml-stackd`**. The Python package namespace is **`ml_stack`**. Environment variables use the **`ML_STACK_`** prefix.

---

## 0. One-sentence definition

**ML-Stack turns an existing coding/AI agent into an autonomous ML research lab that can ingest a challenge, research the best approaches, design a correct validation scheme, run CPU/GPU experiments on pluggable compute backends, compare evidence, iterate through versioned solutions, and return the best reproducible submission without pretending that unmeasured results are real.**

---

# 1. Executive summary

ML-Stack is not another chat application, not a new foundation model, and not a replacement for Codex, Claude Code, ChatGPT, OpenCode, or other agent hosts.

It is a portable **ML capability bundle** composed of:

1. **Agent Skills / workflow instructions**  
   Teach the host agent how to reason about ML tasks, challenges, experimental science, validation, research, and promotion decisions.

2. **A common MCP/tool server**  
   Exposes durable machine actions: data inspection, paper search, web/documentation research, experiment creation, job submission, log retrieval, artifact handling, result comparison, repository operations, and notifications.

3. **A small orchestration/runtime core**  
   Maintains the challenge state machine, experiment ledger, provenance, budgets, resumability, event stream, approvals, and version history.

4. **Compute-provider adapters**  
   Route work to local CPU/GPU, Hugging Face Jobs, Hugging Face sandbox/Spaces, Kaggle batch jobs, Modal, SSH/Slurm, or future providers without changing the scientific workflow.

5. **Thin host adapters**  
   Package the same source-of-truth workflows for Claude Code, Codex, ChatGPT, OpenCode, and generic Agent-Skills/MCP-capable hosts.

6. **A requirements-driven, versioned artifact contract**  
   Produces whatever deliverables the user's `requirements.md` and the platform actually require. Internal promoted versions are always immutable (`v1`, `v2`, `v3`, ...), but exported filenames are not assumed to be `solution.py`, `submission.csv`, or even Python/CSV at all.

The desired experience is:

```text
cd project-or-challenge-folder
/ml-stack
```

The user can walk away. ML-Stack should first persist the user's exact requirements, discover the task, lock the evaluation and deliverable contract, inspect data, research, build a baseline, launch experiments, reject failed hypotheses, promote real improvements, retrain where appropriate, validate every requested deliverable, and leave behind the strongest reproducible artifact set plus a concise research report.

The host agent remains the visible "brain." ML-Stack supplies the **method, memory, tools, execution plane, and discipline**.

---

# 2. Core philosophy

## 2.1 Smart and humble

ML-Stack must optimize for strong results while enforcing epistemic discipline.

It must never turn:

- "this probably improves the score" into "this improves the score";
- an estimated score into a measured score;
- a single lucky split into a robust validation claim;
- a public leaderboard result into proof of generalization;
- an experiment that crashed into a silently altered experiment;
- a paper result on a different dataset into an expected challenge score;
- a model capability guess into a measured resource requirement.

Every important claim must be classified as one of:

- **Measured** — backed by a completed run and evaluator record.
- **Externally observed** — e.g. public leaderboard feedback supplied through an allowed interface.
- **Literature evidence** — backed by a paper/document/source and not yet reproduced here.
- **Estimated** — produced by an explicit estimator.
- **Hypothesis** — not yet tested.
- **Unknown** — insufficient evidence.

A score shown as measured must carry at least:

```text
metric
value
split/protocol
run_id
solution_version
code_hash
data_hash
seed(s)
timestamp
```

## 2.2 Research before expensive experimentation

The system should spend cheap tokens and cheap CPU before expensive GPU hours.

Default order:

```text
Understand -> Validate -> Research -> Baseline -> Cheap probes ->
Promising full runs -> Robustness -> Ensemble/finalize
```

## 2.3 Validation is infrastructure, not an afterthought

A sophisticated model with a bad validation split is worse than a basic model with a faithful validation scheme. ML-Stack therefore treats the validation protocol as a locked artifact that must be created before broad experimentation.

## 2.4 Provider-neutral science

Scientific logic must not depend on where a job runs. A hypothesis should be expressible once and executable locally, on HF Jobs, Kaggle, Modal, or another backend.

## 2.5 Bounded autonomy

"Walk away" does not mean "unbounded spending." ML-Stack must support autonomous operation inside explicit limits for:

- wall-clock time;
- token/API spend;
- GPU/CPU spend;
- provider credits;
- experiment count;
- concurrency;
- maximum run duration;
- maximum retries;
- network permissions;
- destructive repository operations.

## 2.6 No hidden-answer shortcuts

ML-Stack is designed for legitimate ML research and benchmark/challenge solving. It must not ingest held-out answers, infer test targets from prohibited sources, or silently violate challenge rules.

---

# 3. Goals

ML-Stack SHALL:

1. Take a complete ML challenge or project directory as input.
2. Parse the challenge description and implementation constraints.
3. Discover training/test/sample-submission files and auxiliary assets.
4. Infer the target, task type, metric, submission schema, and grouping constraints.
5. Detect whether the task is primarily CPU, GPU, mixed, or unknown.
6. Build a reproducible baseline before advanced optimization.
7. Perform paper-first research using independent research contexts.
8. Search papers, citation graphs, full-text snippets, documentation, web sources, datasets, and working GitHub examples.
9. Translate research findings into ranked, testable hypotheses.
10. Run controlled experiments with explicit parentage and expected outcomes.
11. Support sequential and parallel experimentation.
12. Route jobs to provider backends based on requirements, budget, quota, and availability.
13. Capture logs, metrics, artifacts, failures, and resource usage.
14. Compare runs using statistically and procedurally valid gates.
15. Promote real improvements to immutable internal artifact bundles `vN`, then export exactly the filenames and formats requested by the active requirements contract.
16. Resume after process crashes, laptop shutdowns, network loss, or agent context replacement.
17. Notify the user only when useful: approval required, budget threshold, major failure, target reached, or final completion.
18. Produce a final report explaining what was tried, what worked, what failed, and why the selected solution won.
19. Install from one repository into multiple agent hosts.
20. Preserve feature parity with the pinned ML Intern snapshot while generalizing those capabilities beyond the Hugging Face-only world.

---

# 4. Non-goals

ML-Stack SHALL NOT:

1. Require its own chat frontend.
2. Require users to switch away from their preferred agent host.
3. Replace the host's primary reasoning model by default.
4. Treat the Hugging Face ecosystem as the only supported ML ecosystem.
5. Hardcode one model family as universally best.
6. Optimize against test labels or prohibited leaderboard leakage.
7. mutate the user's repository destructively without an approval policy.
8. imply that free compute is guaranteed.
9. promise identical UX primitives on hosts whose plugin systems differ.
10. hide failed experiments.
11. silently change a validation protocol merely because a result looks worse.
12. overwrite previous promoted versions.
13. copy upstream source code without complying with the applicable licenses and preserving required notices.

---

# 5. User experience

## 5.1 Main command

The zero-configuration path is:

```text
/ml-stack
```

In a challenge directory, this means:

```text
ingest current directory
capture and persist requirements
discover/parse the project or challenge
lock constraints, validation, and required deliverables
research
build v1 baseline
run experiment loop
promote better versions
materialize the required final artifact set
audit everything
report
```

## 5.2 Optional commands

The common skill family SHOULD expose:

```text
/ml-stack
/ml-stack run
/ml-stack inspect
/ml-stack requirements
/ml-stack requirements lock
/ml-stack baseline
/ml-stack research
/ml-stack experiment "<hypothesis>"
/ml-stack status
/ml-stack compare
/ml-stack benchmark
/ml-stack notes
/ml-stack learn
/ml-stack report
/ml-stack resume
/ml-stack stop
/ml-stack doctor
/ml-stack update
```

Host adapters may namespace these commands if required. The common semantic behavior must remain identical.

## 5.3 Example invocation with constraints

```text
/ml-stack run
  target=0.75
  metric=auto
  wall_time=6h
  compute=free-first
  concurrency=4
  max_gpu_jobs=2
  validation=robust
```

Natural-language invocation must also work:

```text
Run ML-Stack on this challenge. Aim for at least 0.75 CV, use free compute
first, don't spend paid credits without asking, and keep iterating until the
target is reached or six hours have passed.
```

## 5.4 Walk-away completion contract

A successful autonomous run ends with the deliverables named in the active requirements contract plus ML-Stack's durable research state.

For a competition task this might be:

```text
solution_v1.py
submission.csv
```

For another project it might be:

```text
train.py
infer.py
model.safetensors
metrics.json
model-card.md
```

For a research benchmark it might be:

```text
benchmark-results.json
report.md
plots/
```

The invariant is not the filename. The invariant is that all requested outputs are generated, audited, and backed by an immutable promoted artifact bundle:

```text
requirements.md
exp/
research/
bench/
notes/
ml-stack-report.md
.ml-stack/state.json
.ml-stack/ledger.sqlite
.ml-stack/artifacts/vN/...
```

The report must include:

- active requirements revision and hash;
- selected internal version;
- requested deliverables and their status;
- measured local score/metrics when applicable;
- validation protocol;
- experiment count;
- important failed hypotheses;
- resource/cost summary;
- reproducibility command;
- known uncertainty;
- exact paths to every final deliverable.

---

# 6. Challenge lifecycle

ML-Stack uses an explicit state machine.

```text
DISCOVER
  |
  v
SPEC_LOCK
  |
  v
DATA_AUDIT
  |
  v
VALIDATION_LOCK
  |
  v
RESEARCH
  |
  v
BASELINE
  |
  v
HYPOTHESIS_QUEUE
  |
  v
EXPERIMENT_LOOP <----+
  |                  |
  +--- reject -------+
  |
  +--- promote ------> VERSIONED_CANDIDATE
                         |
                         v
                   ROBUSTNESS_CHECK
                         |
                         v
                    FINAL_RETRAIN
                         |
                         v
                  SUBMISSION_AUDIT
                         |
                         v
                       DONE
```

All states must be resumable.

## 6.1 DISCOVER

Actions:

- enumerate repository/challenge files;
- identify likely statement/spec documents;
- identify train/test/sample submission;
- inspect file sizes and types without loading huge assets unnecessarily;
- inspect existing baseline code;
- inspect package/environment files;
- detect prior ML-Stack state;
- locate challenge-specific rules.

Outputs:

```text
.ml-stack/discovery.json
.ml-stack/input_manifest.json
```

## 6.2 SPEC_LOCK

The challenge parser converts prose into a machine-readable contract.

Minimum fields:

```yaml
challenge:
  name:
  task_family:
  target:
  target_type:
  prediction_unit:
  metric:
  metric_direction: maximize|minimize
  train_files: []
  test_files: []
  sample_submission:
  id_columns: []
  output_columns: []
  grouping_keys: []
  time_keys: []
  leakage_constraints: []
  implementation_requirements: []
  prohibited_methods: []
  resource_constraints: []
  submission_constraints: []
  notes: []
```

The lock includes the source lines/file spans used to infer each rule.

If a crucial requirement is ambiguous and cannot be safely inferred, autonomous mode may choose the conservative interpretation and record it. It should ask the user only when the ambiguity blocks a valid solution or has material cost/risk.

## 6.3 DATA_AUDIT

The data auditor must inspect:

- row counts and dimensions;
- data types;
- missingness;
- categorical cardinalities;
- duplicates;
- group structure;
- time ordering;
- image/audio/text asset integrity;
- class imbalance;
- target distribution;
- feature distribution shift between train/test;
- suspicious identifier correlations;
- leakage candidates;
- sample-submission schema;
- memory footprint;
- sparsity;
- modality;
- label availability;
- candidate-list or structured-output shape.

Outputs:

```text
.ml-stack/data/profile.json
.ml-stack/data/report.md
.ml-stack/data/leakage_findings.json
```

## 6.4 VALIDATION_LOCK

Before broad experimentation, ML-Stack commits to a validation protocol.

Possible protocols include:

- stratified holdout;
- repeated stratified holdout;
- K-fold;
- stratified K-fold;
- grouped K-fold;
- stratified-group K-fold;
- time-series split;
- blocked temporal split;
- leave-one-group-out;
- nested CV;
- challenge-specific structured split;
- bundle/entity-level split;
- custom reconstruction of the official metric.

Validation lock includes:

```yaml
protocol:
  splitter:
  folds:
  repeats:
  seed:
  grouping:
  stratification:
  temporal_policy:
  metric_implementation:
  aggregation:
  confidence_method:
  rationale:
  leakage_checks:
```

Changing validation later creates a **new validation protocol version**. Results under incompatible protocols must not be directly compared without an explicit bridge experiment.

## 6.5 RESEARCH

The research stage builds a ranked evidence-backed recipe list before costly experiments. See Section 11.

## 6.6 BASELINE

The baseline must be:

- simple;
- correct;
- fast;
- reproducible;
- metric-faithful;
- strong enough to validate the pipeline.

A baseline is promoted to `v1` only after:

1. code runs end to end;
2. local evaluator succeeds;
3. submission passes schema validation;
4. no implementation-rule violation is detected.

## 6.7 HYPOTHESIS_QUEUE

Every experiment begins as a hypothesis object, not an unstructured idea.

```yaml
hypothesis_id: H-0012
parent_version: v3
claim: "Character n-grams should improve this historical-language task."
mechanism: "They capture spelling variation missed by word features."
evidence:
  - type: literature
  - source_id: ...
change:
  component: features
  description: ...
expected_effect:
  metric_delta: positive
  confidence: medium
cost:
  class: cpu-small
  estimated_minutes: 8
risk:
  leakage: low
  implementation: low
decision_rule:
  promote_if: ...
```

## 6.8 EXPERIMENT_LOOP

Default policy:

1. run smoke check;
2. run cheap validation;
3. if promising, run full validation;
4. if promoted, optionally run robustness seeds/folds;
5. update hypothesis queue using evidence.

The scheduler should support independent experiments in parallel while preventing incompatible branches from contaminating each other.

## 6.9 ROBUSTNESS_CHECK

Before final promotion for a high-stakes candidate, check where practical:

- seed sensitivity;
- fold consistency;
- subgroup behavior;
- calibration if relevant;
- resource stability;
- deterministic execution requirements;
- train/inference parity;
- submission reproducibility.

## 6.10 FINAL_RETRAIN

Where the task allows it, train the chosen configuration on all permitted labeled data. Keep final-train artifacts separate from validation artifacts.

## 6.11 SUBMISSION_AUDIT

The auditor verifies:

- exact IDs;
- no missing IDs;
- no extra IDs;
- row order requirements;
- required column names;
- data types;
- value ranges;
- structured-output syntax;
- no NaN/inf unless allowed;
- no index column accidentally saved;
- deterministic output where required;
- challenge implementation requirements;
- no test-label access;
- runnable solution entry point;
- package/import availability;
- time/resource constraints where known.

---

# 7. Versioning and artifact contract

## 7.1 Internal versions are mandatory; exported filenames are requirements-driven

Promoted versions are immutable internal bundles:

```text
v1
v2
v3
...
```

ML-Stack must never assume the exported artifact is named `solution.py`, uses Python, or includes a submission file.

The active `requirements.md` determines the public/exported deliverables. Examples:

```yaml
deliverables:
  - path: solution_v1.py
    kind: executable
  - path: submission.csv
    kind: predictions
```

or:

```yaml
deliverables:
  - path: src/train.py
  - path: src/infer.py
  - path: outputs/model.safetensors
  - path: outputs/metrics.json
```

or simply:

```yaml
deliverables:
  - path: report.md
```

Internal versions remain stable even if the platform requires one fixed final filename. For example, `v5` can be exported as `solution.py` without renaming the historical bundle.

## 7.2 Internal immutable record

Each promoted version stores:

```text
.ml-stack/artifacts/vN/
  manifest.yaml
  requirements.snapshot.md
  requirements.lock.yaml
  config.yaml
  metrics.json
  report.md
  provenance.json
  source/
  deliverables/
  logs/
  models/
  predictions/
```

`manifest.yaml` declares the exact export map:

```yaml
version: v4
exports:
  - from: deliverables/main.py
    to: solution_v1.py
  - from: deliverables/predictions.csv
    to: submission.csv
```

`provenance.json` MUST include:

```json
{
  "version": "v4",
  "parent_version": "v3",
  "promoted_from_run": "run_01J...",
  "requirements_hash": "...",
  "validation_protocol": "val_v1",
  "code_hash": "...",
  "data_manifest_hash": "...",
  "config_hash": "...",
  "seeds": [42],
  "metric": {"name": "...", "value": 0.7421},
  "status": "measured",
  "research_evidence_ids": ["E-14", "E-22"]
}
```

## 7.3 Experiment runs are not versions

A failed or inferior experiment remains in `exp/` and the ledger but does not consume a promoted version.

Example:

```text
v3
 ├─ exp/0017 -> worse
 ├─ exp/0018 -> crashed
 ├─ exp/0019 -> +0.011 -> promote v4
 └─ exp/0020 -> inconclusive
```

## 7.4 Root exports

Root/project deliverables are materialized only from the selected promoted bundle according to the requirements contract.

They may be copies, symlinks, package directories, model files, reports, notebooks, archives, or provider publication actions. The export mechanism must preserve the exact names and formats the user/platform requested.

## 7.5 Requirements are versioned with artifacts

If the user changes requirements mid-project, ML-Stack snapshots the new revision and records which experiments and promoted versions were run under each requirements hash.

A result produced under incompatible requirements must not silently become the final deliverable for the new requirements.

---

# 8. Repository-local state and human-readable lab workspace

ML-Stack uses both visible human-readable folders and hidden machine state.

Recommended default layout:

```text
project/
├─ requirements.md
├─ exp/
│  ├─ README.md
│  ├─ index.md
│  ├─ 0001-baseline/
│  │  ├─ hypothesis.md
│  │  ├─ config.yaml
│  │  ├─ run.md
│  │  ├─ metrics.json
│  │  ├─ notes.md
│  │  └─ artifacts/
│  ├─ 0002-...
│  └─ ...
├─ research/
│  ├─ papers.md
│  ├─ web.md
│  ├─ docs.md
│  ├─ code.md
│  ├─ datasets.md
│  ├─ evidence.jsonl
│  └─ synthesis.md
├─ bench/
│  ├─ models.md
│  ├─ hardware.md
│  ├─ providers.md
│  ├─ runtime.jsonl
│  └─ memory.jsonl
├─ notes/
│  ├─ task.md
│  ├─ data.md
│  ├─ validation.md
│  ├─ decisions.md
│  ├─ failures.md
│  ├─ ideas.md
│  └─ final.md
├─ <user-required final deliverables...>
├─ ml-stack-report.md
└─ .ml-stack/
   ├─ config.toml
   ├─ state.json
   ├─ requirements/
   │  ├─ user.md
   │  ├─ challenge.md
   │  ├─ defaults.md
   │  └─ lock.yaml
   ├─ challenge.yaml
   ├─ input_manifest.json
   ├─ ledger.sqlite
   ├─ events.jsonl
   ├─ locks/
   ├─ research-cache/
   ├─ validation/
   ├─ hypotheses/
   ├─ runs/
   ├─ artifacts/
   │  ├─ v1/
   │  ├─ v2/
   │  └─ ...
   ├─ cache/
   └─ logs/
```

The visible folders are deliberate. They allow a human or a different agent host to inspect the actual research process without decoding SQLite.

`exp/` is the default home of experiments. Every experiment gets a stable numeric directory and is never overwritten.

`research/` is the durable research notebook for papers, web research, documentation, code examples, datasets, and synthesis.

`bench/` stores empirical performance measurements about models, hardware, providers, runtimes, and memory.

`notes/` stores evolving project understanding, decisions, failures, and ideas in plain Markdown.

Large model files should be configurable to an external artifact store rather than forced into the working repository.

---

# 9. High-level architecture

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         HOST AGENT / UI                             │
│  Claude Code | Codex | ChatGPT | OpenCode | Generic Agent Host     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ Agent Skill / Plugin invocation
                               v
┌─────────────────────────────────────────────────────────────────────┐
│                        ML-AGENT SKILL LAYER                         │
│ requirements | research | experiment | benchmark | memory | audit │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ MCP/tool calls
                               v
┌─────────────────────────────────────────────────────────────────────┐
│                         ML-AGENT CORE                               │
│ Orchestrator | State | Event Log | Ledger | Budget | Approvals      │
│ Context | Doom-loop | Provenance | Requirements | Memory | Versions│
└───────────────┬──────────────────────────────┬──────────────────────┘
                │                              │
                v                              v
┌─────────────────────────────┐   ┌───────────────────────────────────┐
│      RESEARCH PLANE         │   │       EXPERIMENT PLANE            │
│ Papers | Web | Docs |       │   │ Challenge parser | profiler |     │
│ GitHub | OpenAPI | Data     │   │ evaluator | experiment compiler   │
│ Independent subagents       │   │ result judge | submission audit   │
└───────────────┬─────────────┘   └─────────────────┬─────────────────┘
                │                                   │
                └────────────────┬──────────────────┘
                                 v
┌─────────────────────────────────────────────────────────────────────┐
│                         COMPUTE BROKER                              │
│ capability match | quota | cost | scheduling | retries | artifacts │
└───────┬─────────┬──────────┬───────────┬──────────────┬────────────┘
        │         │          │           │              │
        v         v          v           v              v
      Local     HF Jobs    Kaggle      Modal       SSH / Slurm
        │         │          │           │              │
        └─────────┴──────────┴───────────┴──────────────┘
                                 │
                                 v
                     Experiment artifacts + metrics
```

---

# 10. Control plane vs execution plane

ML-Stack separates orchestration from heavy compute.

## 10.1 Control plane

Runs where the host agent can access it. Responsibilities:

- task state;
- hypothesis selection;
- tool routing;
- research;
- budget decisions;
- run submission;
- log polling;
- comparison;
- version promotion;
- notifications.

The control plane should be light enough for a laptop or small cloud service.

## 10.2 Execution plane

Runs untrusted/heavy experiment code in isolated environments. Responsibilities:

- dependency installation;
- data staging;
- model training;
- prediction;
- metric computation;
- checkpointing;
- artifact export.

A provider adapter must never be allowed to alter scientific decision logic.

---

# 11. Research engine

The research engine is a first-class subsystem and must meet or exceed the pinned ML Intern research behavior.

## 11.1 Independent context

Research workers run in independent contexts so long paper, GitHub, and documentation traces do not pollute the host agent's primary working context.

A research worker receives:

- a focused research question;
- compact challenge context;
- read-only research tools;
- a token/iteration budget;
- output schema.

It returns a concise evidence package to the orchestrator.

## 11.2 Paper-first default

Default research sequence:

1. **Find anchor papers** for the task/domain.
2. **Find influential and recent work** using citations and references.
3. **Crawl downstream citations** to identify improvements/applications.
4. **Read methodology and experiment sections**, not only abstracts.
5. Extract exact datasets, preprocessing, model architecture, optimizer, LR, scheduler, batch size, epochs/steps, augmentation, regularization, loss, inference strategy, and reported scores.
6. **Attribute results to recipes**, not vague techniques.
7. Discover datasets/models/collections linked to papers.
8. Inspect candidate datasets if external data is permitted.
9. Find working implementation examples.
10. Verify current APIs in official documentation.
11. Convert evidence into ranked, feasible hypotheses for this challenge.

## 11.3 Paper operations

ML-Stack paper tools SHALL expose at least the feature set represented by ML Intern's `hf_papers`:

```text
trending
search
paper_details
read_paper
citation_graph
snippet_search
recommend
find_datasets
find_models
find_collections
find_all_resources
```

Required search controls:

- query;
- date range;
- field/category;
- minimum citations;
- relevance/citation/date sorting;
- result limit.

Required paper reading behavior:

- metadata and abstract;
- table of contents/section listing when available;
- section-specific full text;
- citations;
- references;
- influence/citation intent when a source provides it.

Recommendation behavior should support:

- one seed paper;
- multiple positive papers;
- optional negative papers.

The implementation may combine Hugging Face, arXiv, Semantic Scholar, Crossref/OpenAlex, or future providers behind a normalized schema.

## 11.4 Evidence object

Every useful research finding becomes an evidence object:

```yaml
evidence_id: E-0021
type: paper
source:
  provider: semantic_scholar
  canonical_id: ...
  title: ...
claim: ...
quote_or_excerpt_hash: ...
section: "4 Experiments"
retrieved_at: ...
relevance:
  task: high
  data: medium
  metric: high
confidence: high
recipe:
  dataset: ...
  method: ...
  hyperparameters: ...
  result:
    metric: ...
    value: ...
    benchmark: ...
```

The system should store source excerpts subject to copyright and provider constraints, but the normal synthesis must paraphrase and remain concise.

## 11.5 Required research synthesis

Research output must rank candidate recipes with:

| Field | Requirement |
|---|---|
| Paper | title, identifier, date/venue if known |
| Result | exact reported benchmark/metric |
| Dataset | name, source, size if reported |
| Method | model/training/inference approach |
| Hyperparameters | only those actually recovered |
| What made it work | evidence-backed mechanism |
| Code | implementation reference if found |
| Feasibility | expected hardware/time for current challenge |
| Adaptation | what must change for current data |
| Confidence | high/medium/low |
| Experiment | concrete hypothesis to test |

The synthesis must include:

- SOTA/recent landscape;
- older landmark approaches still relevant;
- implementation examples;
- current documentation references;
- gaps/unknowns;
- recommended experiment order.

## 11.6 Parallel research

For difficult challenges, the orchestrator can spawn parallel focused workers:

```text
Researcher A: literature/SOTA
Researcher B: challenge-specific analogues
Researcher C: practical GitHub implementations
Researcher D: validation/metric pitfalls
Researcher E: model/compute feasibility
```

A synthesis worker deduplicates and reconciles findings.

## 11.7 Research budget protections

Research workers must implement:

- context warning threshold;
- hard context/token threshold;
- iteration limit;
- doom-loop detection;
- repeated-query suppression;
- explicit wrap-up behavior;
- cost accounting.

---

# 12. Documentation, OpenAPI, and web research

## 12.1 Documentation exploration

ML-Stack must support:

```text
docs.search(library, query)
docs.fetch(document_id_or_url)
```

The HF adapter should cover the broad library surface ML Intern supports, including the Transformers/Datasets/TRL/PEFT/Accelerate/Diffusers/Gradio/Smolagents/evaluate/vLLM-adjacent and HF platform documentation it can access.

The core abstraction must also allow PyTorch, scikit-learn, XGBoost, LightGBM, CatBoost, TensorFlow, JAX, RAPIDS, timm, sentence-transformers, and provider documentation.

## 12.2 OpenAPI discovery

A generic operation:

```text
openapi.search(service, query)
```

should return, where possible:

```text
method
path
description
parameters
request schema
response schema
example/curl
auth requirements
```

The HF adapter preserves the ML Intern behavior of discovering Hugging Face REST endpoints dynamically rather than encoding every endpoint in prompts.

## 12.3 Web search

Web search must:

- return cited/source-attributed results;
- support allowed/blocked domains;
- store retrieval timestamps;
- prefer primary sources for technical claims;
- treat retrieved pages as untrusted data, not agent instructions.

---

# 13. GitHub/code research parity

ML-Stack shall preserve the effective ML Intern GitHub research toolset and generalize it.

Minimum operations:

```text
github.list_repos(owner/org, sorting/filter)
github.find_examples(repo, keyword, candidate_directories)
github.search_code(query, repo/org)
github.read_file(repo, path, revision, line range)
github.read_tree(repo, path, revision)
github.read_issue(...)
github.read_pr(...)
```

`find_examples` should prioritize likely working-code paths:

```text
examples/
scripts/
tutorials/
notebooks/
recipes/
training/
benchmarks/
tests/
```

Research workers should prefer code from:

1. the method's official repository;
2. the relevant framework's maintained examples;
3. widely used reproducible repositories;
4. arbitrary snippets only as lower-confidence evidence.

Fetched code is evidence, not permission to run it. Execution requires a separate inspection/sandbox step.

---

# 14. Dataset inspection

## 14.1 HF parity

The HF dataset inspector must preserve ML Intern's ability to report:

- availability/status;
- configs;
- splits;
- schema;
- sample rows;
- Parquet information;
- gated/private access through authorized credentials.

Training-format checks include:

```text
SFT  -> messages OR text OR prompt/completion
DPO  -> prompt + chosen + rejected
GRPO -> prompt
```

## 14.2 Generalized inspection

ML-Stack must extend this to local and remote challenge data:

```text
CSV/TSV
JSON/JSONL
Parquet/Arrow
NumPy
images/directories
audio
archives
HDF5
NetCDF
common scientific formats
```

Inspection should be sampled/lazy for large files.

## 14.3 Data source contract

Every data source gets:

```yaml
source_id:
kind: local|hf|kaggle|remote|generated
license:
allowed_by_challenge:
hash:
size:
schema:
sensitivity:
staging_policy:
```

External data cannot enter experiments until challenge rules permit it.

---

# 15. ML task classifier

ML-Stack should infer one or more task families:

```text
tabular classification
tabular regression
multilabel
ranking
recommendation
sequence-to-sequence
language modeling
token classification
structured prediction
time series
computer vision classification
detection
segmentation
image retrieval/re-ID
audio
graph ML
scientific inverse problems
multimodal
optimization/search
custom metric challenge
```

The classifier uses:

- challenge prose;
- output schema;
- target type;
- data modality;
- metric;
- baseline code;
- shape relationships.

The classification informs research queries and baseline families but never hardcodes the final method.

---

# 16. CPU/GPU requirement inference

A compute planner creates a resource profile before a job runs.

```yaml
resource_profile:
  accelerator: none|gpu|tpu|unknown
  min_vram_gb:
  preferred_vram_gb:
  cpu_cores:
  ram_gb:
  disk_gb:
  expected_runtime:
  network_required:
  multi_gpu:
  checkpointable:
```

Inputs include:

- model parameter count;
- precision;
- batch size;
- optimizer memory;
- sequence/image dimensions;
- dataset size;
- framework;
- training vs inference;
- expected parallelism.

Decision categories:

```text
CPU_SMALL
CPU_LARGE
GPU_SMALL
GPU_MEDIUM
GPU_LARGE
MULTI_GPU
MIXED
UNKNOWN_PROBE_REQUIRED
```

For `UNKNOWN_PROBE_REQUIRED`, ML-Stack runs a small profiling job instead of guessing.

---

# 17. Compute broker

## 17.1 Provider interface

Every compute backend implements a normalized interface.

```python
class ComputeProvider:
    def capabilities(...)
    def quota(...)
    def estimate(...)
    def stage(...)
    def submit(...)
    def status(...)
    def logs(...)
    def inspect(...)
    def cancel(...)
    def artifacts(...)
    def cleanup(...)
```

Optional:

```python
def schedule(...)
def list_schedules(...)
def suspend_schedule(...)
def resume_schedule(...)
def delete_schedule(...)
```

## 17.2 Initial providers

P0/P1 providers:

1. **Local**
   - CPU
   - local GPU if available
   - isolated venv/container optional

2. **Hugging Face Jobs**
   - submit/list/logs/inspect/cancel
   - scheduled-job lifecycle where supported
   - hardware selection
   - secrets/env
   - long-running jobs

3. **Hugging Face sandbox/Space runtime**
   - ephemeral private sandbox
   - CPU auto-use policy
   - explicit accelerator creation
   - filesystem operations

4. **Kaggle**
   - dataset/kernel packaging
   - batch notebook/script submission
   - status/output retrieval
   - CPU/GPU choice subject to account quota
   - no assumption that quota is available

5. **Modal**
   - remote function/job submission
   - CPU/GPU resource profiles
   - artifact/volume strategy
   - no assumption of free credits

6. **SSH / Slurm**
   - generic lab/server integration
   - scheduler job IDs
   - logs/cancel/artifacts

Future adapters may include other clouds, hosted notebooks, or institutional clusters.

## 17.3 Free-first policy

`compute.policy = "free-first"` means:

1. query actual provider capability/quota;
2. prefer zero-marginal-cost capacity;
3. use the least expensive capable backend;
4. do not assume a provider is free because it historically had a free tier;
5. ask before crossing user-defined paid-spend threshold.

## 17.4 Provider scoring

Candidate providers can be ranked by:

```text
capability_fit
estimated_cost
available_quota
startup_latency
expected_runtime
reliability
data_transfer_cost
privacy policy
artifact persistence
checkpoint support
```

Example:

```text
provider_score =
  capability_gate *
  (w1*cost_score +
   w2*latency_score +
   w3*reliability +
   w4*quota_score +
   w5*data_locality)
```

Hard constraints always beat the score.

## 17.5 Job lifecycle

Normalized state:

```text
CREATED
STAGING
QUEUED
RUNNING
SUCCEEDED
FAILED
CANCELLED
TIMED_OUT
ORPHANED
```

The run supervisor must detect provider/API disconnection without immediately declaring the job failed.

## 17.6 Failure adaptation

Examples:

- CUDA OOM -> reduce batch/enable accumulation or select more VRAM if scientifically equivalent.
- Disk full -> clean cache or choose larger disk.
- Transient provider outage -> retry with exponential backoff.
- Preemption -> resume checkpoint if supported.
- Dependency failure -> fix environment and create a child run, never mutate history.
- Hard timeout -> preserve partial logs/artifacts.

Scientific changes caused by a failure must produce a new run configuration.

---

# 18. ML Intern job/sandbox parity requirements

ML-Stack's compute layer must preserve the underlying capabilities represented by ML Intern:

- local `bash/read/write/edit`;
- remote/sandbox `bash/read/write/edit`;
- explicit sandbox creation;
- private sandbox preference;
- CPU and GPU runtimes;
- hardware-flavor selection;
- job run;
- job process/list;
- logs;
- inspect;
- cancel;
- scheduled run;
- scheduled list;
- scheduled inspect;
- scheduled delete;
- scheduled suspend;
- scheduled resume;
- environment variables;
- secret injection;
- namespace/project targeting;
- long-running log handling/retries;
- experiment-tracking/dashboard integration hooks;
- GPU budget/reservation tracking.

Provider names and accelerator flavors are intentionally not hardcoded into the scientific core because providers change.

---

# 19. Experiment model

## 19.1 Experiment object

```yaml
experiment_id: EXP-0041
hypothesis_id: H-0019
parent_version: v3
validation_protocol: val_v1
changes:
  - path: model.type
    from: lightgbm
    to: catboost
controlled_variables:
  seed: 42
  featureset: f7
resources:
  class: GPU_SMALL
budget:
  max_runtime: 45m
stages:
  - smoke
  - medium
  - full
promotion_rule:
  metric_delta_min: 0.003
  require_fold_consistency: true
```

## 19.2 One-main-variable rule

By default, each experiment changes one major conceptual variable. Bundled changes are allowed when:

- the components are inseparable;
- the literature recipe requires the combination;
- or the run is explicitly marked `compound`.

This improves causal interpretation of results.

## 19.3 Multi-fidelity ladder

Default:

```text
L0: static/code/config checks
L1: tiny-data smoke run
L2: 1 split / reduced steps
L3: full locked validation
L4: multi-seed or repeated robustness
L5: final full-data train
```

Only promising candidates advance.

## 19.4 Experiment queue policy

Candidate ranking can combine:

```text
expected_gain
evidence_strength
novelty
information_gain
runtime
cost
risk
dependency readiness
```

This is a bandit-like scheduling problem, but the initial implementation can use a transparent heuristic score.

## 19.5 Search strategies

Supported strategies:

- manual/research-generated hypotheses;
- grid;
- random;
- Bayesian optimization;
- successive halving;
- Optuna-compatible studies;
- population-based search where appropriate.

Hyperparameter search does not replace architectural/research hypotheses.

---

# 20. Result judge

The Result Judge is the only component allowed to label an experiment an "improvement."

Checks:

1. same compatible validation protocol;
2. evaluator completed;
3. metric direction known;
4. score delta exceeds configured practical threshold;
5. no failed folds silently dropped;
6. no invalid predictions;
7. no leakage/compliance failure;
8. uncertainty considered where enough repeats exist;
9. resource increase considered if optimization target includes cost.

Possible decisions:

```text
PROMOTE
REJECT
INCONCLUSIVE
RETRY_TECHNICAL
ROBUSTNESS_REQUIRED
INVALID_COMPARISON
```

For a simple one-split challenge, the judge can be less statistical but must say so.

---

# 21. Validation and leakage safeguards

ML-Stack must actively test for:

- target in features;
- post-outcome features;
- duplicated entities across folds;
- group leakage;
- temporal leakage;
- near-duplicate text/image leakage;
- file path/ID encodings that expose labels;
- preprocessing fitted on all data;
- target encoding without out-of-fold construction;
- normalization using test labels;
- test prediction feedback used as training labels;
- hidden answer files;
- accidental sample-submission target reuse.

The rules engine must distinguish:

- legitimate transductive use of unlabeled test features;
- prohibited use of held-out answers;
- challenge-specific allowances.

If the challenge explicitly forbids external data, pretrained models, handcrafted rules, ensembles, test-time adaptation, or similar methods, the compliance layer must encode and enforce that.

---

# 22. Challenge compliance engine

Challenge prose often contains constraints beyond metric/data.

The compliance engine creates executable checks where possible:

```yaml
rule_id: R-07
source: challenge.md:143-149
type: prohibited_method
rule: "No external pretrained models"
check:
  static_imports: [...]
  artifact_metadata: [...]
severity: fatal
```

Checks include:

- required libraries/methods;
- prohibited libraries/methods;
- CPU-only/GPU restrictions;
- no internet at evaluation;
- deterministic execution;
- source inspectability;
- no subprocess/dynamic code if prohibited;
- no held-out answer access;
- time/memory limit;
- exact output type/format.

A solution cannot be promoted to final if a fatal compliance check is unresolved.

---

# 23. Baseline library

ML-Stack should maintain baseline templates by task family, but templates are starting points, not hardcoded answers.

Examples:

### Tabular
- constant/prior;
- linear/logistic;
- HistGradientBoosting;
- LightGBM/XGBoost/CatBoost if available/permitted;
- simple preprocessing pipelines.

### Text/NLP
- majority/simple heuristic only as metric sanity check;
- TF-IDF word/character + linear model;
- compact pretrained encoder if permitted and compute-appropriate;
- seq2seq baseline for generative targets.

### Vision
- image-statistics sanity baseline;
- pretrained small backbone if permitted;
- augmentation-light baseline.

### Ranking/recommendation
- prevalence/popularity sanity baseline;
- pairwise/listwise classical baseline;
- learned compatibility model.

### Scientific/custom
- direct physics/domain baseline if the task supplies equations;
- classical inverse/optimization baseline;
- learned residual only after baseline is correct.

Every template must expose a common train/evaluate/predict interface.

---

# 24. Model-development capabilities

ML-Stack must support both conventional ML and modern deep learning.

Expected ecosystem adapters include:

- scikit-learn;
- XGBoost;
- LightGBM;
- CatBoost;
- PyTorch;
- Transformers;
- Datasets;
- PEFT;
- TRL;
- Accelerate;
- timm;
- sentence-transformers;
- relevant scientific Python libraries.

LLM training workflows should include, when appropriate:

- SFT;
- DPO;
- GRPO;
- LoRA;
- QLoRA;
- full fine-tuning;
- distillation/evaluation workflows.

These are capabilities, not assumptions about challenge solutions.

---

# 25. Tool/MCP surface

The stable public namespace should be provider-neutral.

Representative P0 tool groups:

## 25.1 Challenge

```text
mlagent.challenge.ingest
mlagent.challenge.inspect
mlagent.challenge.rules
mlagent.challenge.status
```

## 25.2 Data

```text
mlagent.data.list
mlagent.data.profile
mlagent.data.sample
mlagent.data.schema
mlagent.data.compare_train_test
mlagent.data.leakage_scan
mlagent.data.inspect_hf
```

## 25.3 Validation

```text
mlagent.validation.propose
mlagent.validation.lock
mlagent.validation.evaluate
mlagent.validation.compare
```

## 25.4 Research

```text
mlagent.research.spawn
mlagent.research.status
mlagent.research.synthesize

mlagent.paper.trending
mlagent.paper.search
mlagent.paper.details
mlagent.paper.read
mlagent.paper.citations
mlagent.paper.snippets
mlagent.paper.recommend
mlagent.paper.find_datasets
mlagent.paper.find_models
mlagent.paper.find_collections
mlagent.paper.find_resources

mlagent.docs.search
mlagent.docs.fetch
mlagent.openapi.search
mlagent.web.search

mlagent.github.list_repos
mlagent.github.find_examples
mlagent.github.search_code
mlagent.github.read_file
```

## 25.5 Planning

```text
mlagent.plan.get
mlagent.plan.update
mlagent.hypothesis.create
mlagent.hypothesis.list
mlagent.hypothesis.rank
```

## 25.6 Experiments

```text
mlagent.experiment.create
mlagent.experiment.run
mlagent.experiment.list
mlagent.experiment.inspect
mlagent.experiment.compare
mlagent.experiment.cancel
mlagent.experiment.promote
```

## 25.7 Compute

```text
mlagent.compute.providers
mlagent.compute.capabilities
mlagent.compute.quota
mlagent.compute.estimate
mlagent.compute.submit
mlagent.compute.status
mlagent.compute.logs
mlagent.compute.inspect
mlagent.compute.cancel
mlagent.compute.artifacts
mlagent.compute.schedule
mlagent.compute.schedule_list
mlagent.compute.schedule_suspend
mlagent.compute.schedule_resume
mlagent.compute.schedule_delete
```

## 25.8 Files/artifacts

```text
mlagent.fs.read
mlagent.fs.write
mlagent.fs.edit
mlagent.shell.exec

mlagent.artifact.list
mlagent.artifact.read
mlagent.artifact.publish
mlagent.version.list
mlagent.version.inspect
mlagent.version.promote
```

## 25.9 Repositories

```text
mlagent.hf.files
mlagent.hf.repo_git
mlagent.repo.branch
mlagent.repo.tag
mlagent.repo.pr
```

HF-specific aliases may be supplied for feature parity.

## 25.10 Notifications/traces

```text
mlagent.notify
mlagent.trace.status
mlagent.trace.export
mlagent.session.resume
mlagent.session.interrupt
mlagent.session.undo
```

The MCP server should expose a stable schema; Skills should invoke tools rather than reimplementing mechanics in prose.

---

# 26. Plan/todo behavior

ML Intern exposes a plan tool for multi-step task tracking. ML-Stack preserves this capability with a structured plan model:

```yaml
items:
  - id: P1
    title: Lock metric
    status: completed
  - id: P2
    title: Build baseline
    status: in_progress
  - id: P3
    title: Research neural approaches
    status: pending
```

Statuses:

```text
pending
in_progress
blocked
completed
cancelled
```

The challenge state machine is authoritative; the plan is its user/agent-facing projection.

---

# 27. Session/runtime behavior

The runtime must preserve the robust agent mechanics represented in ML Intern.

## 27.1 Context management

Features:

- count/estimate context use;
- compact when near threshold;
- retain system contract, challenge lock, validation lock, active plan, promoted version, unresolved failures, and current hypotheses;
- summarize old tool output;
- never compact away provenance references needed for claims.

## 27.2 Prompt caching

Where model/provider APIs support it, stable prefixes should be cacheable:

- system behavior;
- tool definitions;
- challenge contract;
- validation contract.

Caching is an optimization, never a correctness dependency.

## 27.3 Reasoning-effort/model capability probing

Where the host/provider exposes model effort controls, ML-Stack may probe supported levels and select appropriate effort.

Default:

- cheap research subqueries may use a cheaper model or capped effort;
- challenge decisions and failure analysis may use higher effort;
- host model remains the default brain.

The plugin must not silently replace the user's host model unless configuration explicitly allows subagent model routing.

## 27.4 Model switching/local models

For parity with ML Intern, the standalone core should be able to call OpenAI-compatible model endpoints through a provider abstraction, including local services such as Ollama/vLLM/LM Studio/llama.cpp-style endpoints when configured.

In native host mode this is optional; the host can remain the only LLM.

## 27.5 Doom-loop detection

Detect:

- repeated identical tool calls;
- repeated failures with unchanged inputs;
- cyclical edit/test/revert patterns;
- repeated provider submission of identical failing runs;
- research loops returning the same sources.

Response:

```text
1. stop repeating;
2. summarize observed loop;
3. change strategy or escalate;
4. notify/ask only if no safe alternative exists.
```

## 27.6 Approval policy

Actions are classified:

```text
READ_ONLY
LOCAL_WRITE
REMOTE_WRITE
COMPUTE_FREE_OR_PREAPPROVED
COMPUTE_PAID
DESTRUCTIVE
EXTERNAL_PUBLISH
SECRET_SCOPE_CHANGE
```

Autonomous mode may preapprove classes within configured budgets. Destructive or spend-threshold-crossing actions remain gated unless the user explicitly opts in.

## 27.7 Cost estimation

Before costly operations, estimate where possible:

- LLM token spend;
- provider compute spend;
- expected GPU time;
- storage/egress;
- experiment count.

Actual usage is recorded separately from estimates.

## 27.8 Autonomous / YOLO-style budget

ML-Stack should support an autonomous budget mode similar in spirit to ML Intern's bounded autonomous execution.

Example:

```toml
[autonomy]
enabled = true
max_wall_time = "8h"
max_llm_usd = 5.0
max_compute_usd = 0.0
max_gpu_hours = 6.0
max_experiments = 40
```

When a threshold is reached, the system pauses safely, preserves state, and requests approval rather than overrunning silently.

## 27.9 Secret redaction

Before logs/traces/research context are persisted or uploaded, redact:

- API keys;
- bearer tokens;
- cloud credentials;
- private URLs with embedded credentials;
- `.env` secrets;
- provider-specific secret values.

Never send secrets to the LLM unless a tool operation truly requires a token and the token can be injected outside model-visible arguments.

---

# 28. Session persistence, resume, interrupt, and undo

## 28.1 Persistence

After every state-changing operation, persist:

```text
event
state snapshot pointer
run/provider IDs
pending approvals
active budgets
artifact references
```

## 28.2 Resume

`/ml-stack resume` should:

1. load latest consistent state;
2. reconcile remote jobs;
3. detect jobs that completed while offline;
4. retrieve logs/artifacts;
5. continue the state machine.

## 28.3 Interrupt

An interrupt should stop agent planning immediately but not blindly kill remote training. The policy should ask/configure whether active jobs are:

- left running;
- checkpointed/cancelled;
- cancelled immediately.

## 28.4 Undo

Undo is for reversible local/control-plane mutations such as plan/status/file edits. It must not pretend to undo an external irreversible action. Remote operations require compensating actions.

---

# 29. Event system

Append-only event records make UI integration, resumption, and debugging host-independent.

Preserve equivalents of ML Intern's event concepts:

```text
processing
ready
assistant_chunk
assistant_message
assistant_stream_end
tool_call
tool_output
tool_log
tool_state_change
approval_required
turn_complete
error
interrupted
compacted
undo_complete
shutdown
```

Add ML-specific events:

```text
challenge_discovered
challenge_locked
data_profiled
leakage_found
validation_proposed
validation_locked
research_started
research_completed
evidence_added
hypothesis_created
experiment_queued
experiment_submitted
experiment_started
metric_reported
experiment_completed
experiment_failed
comparison_completed
version_promoted
target_reached
final_retrain_started
submission_validated
submission_ready
budget_warning
budget_exhausted
```

Event schema:

```json
{
  "event_id": "...",
  "session_id": "...",
  "timestamp": "...",
  "event_type": "metric_reported",
  "actor": "experiment-supervisor",
  "run_id": "...",
  "data": {},
  "redacted": true
}
```

---

# 30. Experiment ledger

SQLite is the default durable ledger.

Core tables:

```text
sessions
events
challenge_specs
validation_protocols
evidence
papers
hypotheses
experiments
runs
metrics
artifacts
versions
compute_jobs
costs
approvals
notifications
```

The ledger is the source of truth for experiment history. Markdown reports are generated views.

---

# 31. SFT/trajectory tagging parity

ML Intern tags session trajectories for downstream analysis. ML-Stack should preserve and generalize this.

Tag namespaces SHOULD include:

```text
tool:<name>
outcome:<completed|errored|interrupted|ongoing|doom_loop|context_exceeded>
job:<submitted|succeeded|failed|multi|oom|published>
provider:<local|hf_jobs|hf_sandbox|kaggle|modal|ssh|slurm|...>
gpu:<none|family|multi>
sandbox:<created|gpu|cpu|long_lived>
feedback:<up|down|mixed|none>
model:<family>
turns:<short|medium|long>
cost:<low|med|high>
task:<training|inference|data_prep|research_only|challenge>
challenge:<family>
version:<vN>
```

Provider-specific compatibility tags such as `hf_job:*` may be emitted when relevant.

Tags are metadata only; they must not mutate experiment behavior.

---

# 32. Artifact and hub/repository management

## 32.1 HF repository files parity

The HF adapter must support reading and writing files in:

- model repositories;
- dataset repositories;
- Spaces.

## 32.2 HF git-like parity

The adapter must preserve operations represented by ML Intern:

### Branches

```text
create_branch
delete_branch
list_refs
```

### Tags

```text
create_tag
delete_tag
```

### Pull requests/discussions

```text
create_pr
list_prs
get_pr
merge_pr
close_pr
comment_pr
change_pr_status
```

### Repository

```text
create_repo
update_repo
```

Support:

- model/dataset/space repository types;
- private/public;
- gated settings where provider supports them;
- Space SDK selection where relevant.

Destructive operations require approval according to policy.

## 32.3 Generic Git hosting

GitHub/Git operations should be delegated to the host's connected tools when available rather than maintaining redundant authentication.

---

# 33. Notifications

ML-Stack must preserve ML Intern's out-of-band notification concept but make it provider-neutral.

P0 notification events:

```text
approval_required
fatal_error
budget_warning
target_reached
turn_or_batch_complete
final_submission_ready
```

Adapters:

- Slack;
- generic webhook;
- host-native notification where available.

Optional later:

- Discord;
- email;
- mobile push.

The notification tool is callable by the orchestrator and specialist agents, but notification spam must be rate-limited/deduplicated.

---

# 34. Tracking and dashboards

Experiment tracking is optional and adapter-based.

First-class integrations may include:

- Trackio;
- local ML-Stack dashboard export;
- Weights & Biases;
- MLflow.

The core must not require an external tracking service. All critical metrics remain in the local ledger.

When Trackio is configured, preserve the ability to create/seed a dashboard link for remote runs rather than waiting for the user to discover it manually.

---

# 35. ML Intern parity matrix

The parity target is defined against the pinned repository snapshot named at the top of this document. New upstream ML Intern features are not silently ignored; see Section 36.

| ML Intern capability | ML-Stack requirement | Priority / treatment |
|---|---|---|
| Interactive CLI | Host agent provides interaction; optional `ml-stack` CLI for debugging | P0 equivalent |
| Headless execution | `ml-stack run` and host-triggered unattended workflow | P0 |
| `--model` style selection | Host model by default; optional subagent/provider model routing | P1 |
| Local OpenAI-compatible models | Optional LLM provider adapter, incl. local endpoints | P1 |
| Local filesystem `bash` | `mlagent.shell.exec` | P0 |
| Local `read` | `mlagent.fs.read` | P0 |
| Local `write` | `mlagent.fs.write` | P0 |
| Local `edit` | `mlagent.fs.edit` | P0 |
| Remote sandbox filesystem tools | Same operations through execution provider | P0 |
| Sandbox creation | Compute broker sandbox API | P0 |
| Private CPU sandbox auto-use | Provider policy can auto-select isolated CPU | P1 |
| Explicit GPU sandbox | Resource planner + sandbox provider | P0 |
| HF Jobs `run` | provider `submit` | P0 |
| HF Jobs `ps` | provider job list/status | P0 |
| HF Jobs `logs` | provider logs | P0 |
| HF Jobs `inspect` | provider inspect | P0 |
| HF Jobs `cancel` | provider cancel | P0 |
| Scheduled run | optional provider scheduler | P1 |
| Scheduled list | optional provider scheduler | P1 |
| Scheduled inspect | optional provider scheduler | P1 |
| Scheduled delete | optional provider scheduler | P1 |
| Scheduled suspend | optional provider scheduler | P1 |
| Scheduled resume | optional provider scheduler | P1 |
| HF hardware selection | normalized resource profiles | P0 |
| Long-running job retry/log behavior | Run Supervisor | P0 |
| HF token/access handling | Credential adapters/scoped secrets | P0 |
| HF router/model catalog | optional LLM provider catalog | P1 |
| Hub artifacts | generic artifact registry + HF adapter | P0 |
| `hf_inspect_dataset` | generalized data inspector + HF adapter | P0 |
| SFT format validation | dataset format validator | P0 |
| DPO format validation | dataset format validator | P0 |
| GRPO format validation | dataset format validator | P0 |
| `explore_hf_docs` | docs search | P0 |
| `fetch_hf_docs` | docs fetch | P0 |
| dynamic HF OpenAPI search | generic OpenAPI search + HF adapter | P0 |
| `hf_papers: trending` | paper.trending | P0 |
| paper search | paper.search | P0 |
| paper details | paper.details | P0 |
| paper section reading | paper.read | P0 |
| citation graph | paper.citations | P0 |
| full-text snippet search | paper.snippets | P0 |
| paper recommendations | paper.recommend | P0 |
| linked dataset discovery | paper.find_datasets | P0 |
| linked model discovery | paper.find_models | P0 |
| linked collection discovery | paper.find_collections | P0 |
| parallel linked-resource discovery | paper.find_resources | P0 |
| Web search | web.search | P0 |
| GitHub find examples | github.find_examples | P0 |
| GitHub list repos | github.list_repos | P0 |
| GitHub read file/ranges | github.read_file | P0 |
| HF repo files | HF file adapter | P0 |
| HF repo branches | HF repo adapter | P1 |
| HF repo tags | HF repo adapter | P1 |
| HF repo PR lifecycle | HF repo adapter | P1 |
| HF repo create/update | HF repo adapter | P1 |
| Plan tool | structured plan | P0 |
| Notify tool | generic notify adapter | P0 |
| Research subagent | independent paper-first research workers | P0 |
| Research read-only allowlist | explicit research tool capability set | P0 |
| Research context isolation | subagent/forked context | P0 |
| Research iteration/context caps | worker budgets | P0 |
| Parallel research status | event-stream status | P0 |
| MCP tool loading | MCP client/server bridge | P0 |
| MCP env interpolation | secure config interpolation | P0 |
| MCP blocked/reserved tool names | namespace and policy validation | P0 |
| ToolRouter | provider-neutral tool registry/router | P0 |
| OpenAPI dynamic tool registration | dynamic service catalogs | P1 |
| ContextManager | context budget + compaction | P0 |
| Auto-compaction | durable state-aware compactor | P0 |
| Prompt caching | provider-dependent cache support | P1 |
| Doom-loop detector | control-plane loop guard | P0 |
| Approval policy | action classes and gates | P0 |
| Cost estimation | LLM/compute cost estimator | P0 |
| Autonomous/Yolo budget pause | bounded autonomous mode | P0 |
| Reasoning effort probe | host/provider capability probe | P1 |
| LLM parameter normalization | LLM adapter | P1 |
| Model switching | optional host/subagent router | P1 |
| Secret redaction | persistence/tool-output redactor | P0 |
| Session object | ML-Stack session/state object | P0 |
| Session persistence | SQLite + event log | P0 |
| Session resume | reconciliation/resume | P0 |
| Session uploader | optional trace exporter | P1 |
| Session trace auto-storage | local private ledger by default | P0 |
| Private trace upload | opt-in remote trace sink | P1 |
| Public/private trace sharing | explicit export/share command | P1 |
| Telemetry | local telemetry + opt-in remote sink | P0 |
| SFT trajectory tagger | generalized session tags | P1 |
| Interrupt | safe interrupt semantics | P0 |
| Undo | reversible control-plane changes | P1 |
| Streaming assistant events | host adapter/event bus | P0 |
| Tool call/output events | event bus | P0 |
| Tool log/state events | event bus | P0 |
| Approval events | event bus | P0 |
| Completion/error events | event bus | P0 |
| Compaction events | event bus | P0 |
| Slack status notifications | Slack adapter | P1 |
| Agent-triggered notification | notify tool | P0 |
| Trackio integration/seeding | tracking adapter | P1 |
| Web backend/session manager | no custom UI required; remote daemon exposes equivalent service APIs | P1 service |
| HF OAuth flow | connector/credential layer where remote daemon needs it | P1 |
| Frontend terminal/chat UI | intentionally replaced by host UI | N/A by design |
| CLI visual effects/typewriter display | not required; host-native status rendering | N/A presentation |
| Backend/frontend local dev stack | only needed for optional remote service/admin UI | N/A core |
| Tests for sandbox auto-start | equivalent provider contract tests | P0 |
| Heartbeat handling | run supervisor heartbeat | P0 |
| Compaction loop break | loop/compaction guards | P0 |
| No-tool continuation guard | agent progress guard | P0 |
| Messaging tests | notification contract tests | P1 |
| Personal trace repo behavior | configurable private trace sink | P1 |

**Parity rule:** A feature may be marked `N/A by design` only if its *function* is supplied by the host or is presentation-only. It cannot be removed merely because implementing it is inconvenient.

---

# 36. Upstream ML Intern parity scanner

"Don't leave a feature behind" must be enforceable rather than a one-time promise.

The repository should include:

```text
tools/parity/ml_intern_snapshot.yaml
tools/parity/scan_ml_intern.py
docs/parity/ml-intern.md
```

`ml_intern_snapshot.yaml` stores:

```yaml
upstream: huggingface/ml-intern
snapshot_commit: b0d6752723d17ef2ea7a54f5aeb63abebba99e47
tracked_surfaces:
  - agent/tools
  - agent/core
  - agent/context_manager
  - agent/messaging
  - agent/sft
  - backend
  - README.md
```

The scanner should:

1. fetch an explicitly requested upstream revision;
2. enumerate tool specs, operations, CLI flags, event names, important core modules, and documented user-facing capabilities;
3. compare them against `docs/parity/ml-intern.md`;
4. flag unclassified additions/removals;
5. fail parity CI when a new upstream feature has no mapping.

This avoids claiming eternal parity with a moving project. ML-Stack can state exact parity against a pinned snapshot and make upstream drift visible.

---

# 37. gstack-inspired packaging principles

ML-Stack adopts the useful deployment pattern, not gstack's product domain.

Principles:

1. **One repository.**
2. **One setup command.**
3. **Skills are ordinary inspectable files.**
4. **Host adapters are generated from one canonical workflow source.**
5. **Supporting binaries/MCP tools ship beside skills.**
6. **Host detection is automatic but overridable.**
7. **Team/project installs are supported.**
8. **Updates are simple and non-destructive.**
9. **Adding a host is data/config-driven where possible.**
10. **The tool behaves like a set of specialists, not one giant prompt.**

---

# 38. Proposed repository structure

```text
ml-stack/
├─ README.md
├─ LICENSE
├─ NOTICE
├─ spec.md
├─ pyproject.toml
├─ uv.lock
├─ setup
├─ bin/
│  ├─ ml-stack
│  └─ ml-stackd
├─ core/
│  ├─ orchestrator/
│  ├─ challenge/
│  ├─ validation/
│  ├─ experiments/
│  ├─ research/
│  ├─ compute/
│  ├─ artifacts/
│  ├─ events/
│  ├─ ledger/
│  ├─ approvals/
│  ├─ budgets/
│  ├─ context/
│  ├─ redaction/
│  └─ telemetry/
├─ providers/
│  ├─ local/
│  ├─ huggingface_jobs/
│  ├─ huggingface_sandbox/
│  ├─ kaggle/
│  ├─ modal/
│  ├─ ssh/
│  └─ slurm/
├─ tools/
│  ├─ papers/
│  ├─ docs/
│  ├─ openapi/
│  ├─ web/
│  ├─ github/
│  ├─ datasets/
│  ├─ repositories/
│  ├─ notifications/
│  └─ parity/
├─ mcp/
│  ├─ server.py
│  ├─ schemas/
│  └─ auth/
├─ skills/
│  ├─ ml-stack/
│  │  └─ SKILL.md
│  ├─ ml-stack-research/
│  │  └─ SKILL.md
│  ├─ ml-stack-experiment/
│  │  └─ SKILL.md
│  ├─ ml-stack-audit/
│  │  └─ SKILL.md
│  └─ references/
├─ agents/
│  ├─ challenge-analyst.md
│  ├─ researcher.md
│  ├─ data-scientist.md
│  ├─ experimenter.md
│  ├─ skeptic.md
│  ├─ evaluator.md
│  ├─ compliance-auditor.md
│  └─ release-auditor.md
├─ adapters/
│  ├─ claude-code/
│  ├─ codex/
│  ├─ chatgpt/
│  ├─ opencode/
│  └─ generic/
├─ manifests/
│  ├─ plugin/
│  └─ mcp/
├─ templates/
│  ├─ baseline/
│  ├─ reports/
│  └─ configs/
├─ scripts/
│  ├─ install/
│  ├─ migrate/
│  └─ doctor/
├─ tests/
│  ├─ unit/
│  ├─ provider_contract/
│  ├─ integration/
│  ├─ replay/
│  ├─ host_adapters/
│  └─ fixtures/
└─ docs/
   ├─ architecture.md
   ├─ adding-a-host.md
   ├─ adding-a-provider.md
   ├─ security.md
   └─ parity/
      └─ ml-intern.md
```

---

# 39. Installer

The canonical install should feel like:

```bash
git clone <ml-stack-repository> ~/ml-stack
cd ~/ml-stack
./setup
```

## 39.1 Setup behavior

`./setup`:

1. checks prerequisites;
2. creates/updates an isolated core environment;
3. builds or installs `ml-stack` / `ml-stackd`;
4. detects supported agent hosts;
5. asks or follows flags for global/project install;
6. installs/generates skills;
7. registers the MCP server;
8. installs host plugin manifests where supported;
9. creates configuration skeleton;
10. runs `ml-stack doctor`;
11. never overwrites user configuration without backup/merge.

Flags:

```text
./setup
./setup --host claude-code
./setup --host codex
./setup --host chatgpt
./setup --host opencode
./setup --host all
./setup --project
./setup --global
./setup --dry-run
./setup --uninstall
./setup --update
```

## 39.2 Idempotence

Running setup repeatedly must be safe.

The installer records:

```text
installed version
host adapters
files created
config patches
MCP registrations
```

Uninstall removes only managed entries.

## 39.3 Team mode

A project can pin ML-Stack behavior/config without vendoring the full implementation.

Example:

```text
.ml-stack-project.toml
AGENTS.md / CLAUDE.md pointer
```

Optional policy:

```toml
[ml_stack]
required_version = ">=0.4,<0.5"
required = true
```

---

# 40. Host adapters

## 40.1 Claude Code

Target a native plugin layout where appropriate:

```text
.claude-plugin/plugin.json
skills/
agents/
hooks/
.mcp.json
settings.json
bin/
```

Use Skills for the workflow and MCP for durable actions. Specialist research can use forked/subagent contexts.

Project and personal installations should both be supported.

## 40.2 OpenAI Codex

Install Agent Skills into the Codex skill location supported by the host and register the local MCP/tool service where available.

The Codex adapter should include:

- canonical `/ml-stack` skill;
- research skill;
- audit skill;
- AGENTS.md integration guidance;
- MCP registration;
- environment/permission guidance.

The installer may generate host/model-specific compact instructions, but the canonical scientific policy remains shared.

## 40.3 ChatGPT

Package ML-Stack as an OpenAI plugin/app-compatible bundle consisting of:

- Skills/instructions;
- MCP-backed tools/app connection;
- templates/configuration guidance.

Important deployment distinction:

- local coding hosts can speak to a local MCP process;
- ChatGPT integrations may require a reachable remote MCP service or supported secure tunnel/connector path.

Therefore `ml-stackd` must be deployable remotely with authentication. The ChatGPT adapter should never require the user to run a separate ML-Stack chat UI.

Because ChatGPT capabilities/plans can differ, installer/doctor must detect supported tool actions instead of assuming all accounts can perform writes.

## 40.4 OpenCode

Use:

- standard Agent Skills;
- OpenCode-compatible skill location;
- native plugin hooks/tools where useful;
- MCP registration in OpenCode configuration.

Where OpenCode can read Claude-compatible skills, the installer should reuse/generated-link common files rather than fork the workflow.

## 40.5 Generic host

Any host that can read instructions but not Skills gets a generated compact `AGENTS.md`-style digest plus access to the MCP server.

Any host with MCP but no skill system can invoke:

```text
mlagent.challenge.ingest
mlagent.challenge.status
...
```

and use the canonical workflow instructions from a static prompt document.

---

# 41. One source of truth for skills

Do not maintain four manually diverging versions of the ML workflow.

Canonical representation:

```text
skills-src/
  ml-stack.md
  research.md
  experiment.md
  audit.md
```

Build step generates:

```text
Claude SKILL.md
Codex skill
OpenCode skill
OpenAI plugin skill manifest
generic digest
```

Host-specific additions are small overlays.

CI should render all adapters and fail on uncommitted generated drift.

---

# 42. Specialist roles

The primary host agent orchestrates specialist roles.

## 42.1 Challenge Analyst

Owns:

- spec parsing;
- metric;
- target;
- submission contract;
- rules;
- task family;
- ambiguity register.

Cannot start expensive experiments.

## 42.2 Researcher

Owns:

- papers;
- citations;
- docs;
- GitHub examples;
- dataset/resource discovery;
- recipe extraction.

Read-only by default.

## 42.3 Data Scientist

Owns:

- profiling;
- split design;
- leakage analysis;
- baseline recommendation;
- feature/model diagnostics.

## 42.4 Experimenter

Owns:

- turning hypotheses into runnable configs;
- staging jobs;
- monitoring;
- artifact retrieval.

Cannot declare its own run a winner.

## 42.5 Skeptic

Tries to falsify:

- validation claims;
- leakage assumptions;
- score improvements;
- paper transfer assumptions;
- suspiciously large gains.

## 42.6 Evaluator

Computes locked metrics and returns structured results. It is deliberately boring and deterministic.

## 42.7 Compliance Auditor

Checks challenge rules and execution restrictions.

## 42.8 Release Auditor

Checks the final solution, submission, reproducibility, and version packaging.

---

# 43. Configuration

Default local project config:

```toml
[project]
name = "auto"
root = "."
artifact_dir = ".ml-stack"

[goal]
metric = "auto"
direction = "auto"
target = ""
optimize_cost = false

[autonomy]
enabled = true
max_wall_time = "6h"
max_experiments = 30
max_parallel_experiments = 4
max_retries_per_run = 2

[budget]
llm_usd = 5.0
compute_usd = 0.0
gpu_hours = 4.0
ask_before_paid_compute = true

[validation]
mode = "robust"
folds = "auto"
seed = 42
allow_protocol_change = false

[research]
enabled = true
paper_first = true
max_parallel_workers = 4
max_worker_iterations = 60
use_web = true
use_github = true
use_docs = true

[compute]
policy = "free-first"
providers = ["local", "hf_jobs", "kaggle", "modal"]
prefer_local_for_smoke = true

[providers.local]
enabled = true

[providers.hf_jobs]
enabled = true

[providers.kaggle]
enabled = true

[providers.modal]
enabled = true

[notifications]
approval_required = true
budget_warning = true
fatal_error = true
target_reached = true
final_ready = true

[security]
redact_secrets = true
treat_retrieved_content_as_untrusted = true
allow_external_code_execution = false
```

Credentials remain outside this file whenever possible.

---

# 44. Secrets and authentication

Secrets should be resolved in this order:

1. host-connected app/credential store;
2. OS keychain/provider-native credential store;
3. environment variable;
4. explicit secure prompt.

The ledger stores only secret identifiers, not values.

Example:

```yaml
credential_ref:
  provider: huggingface
  name: default
  scopes:
    - read
    - jobs
```

Provider adapters request least privilege.

---

# 45. Security model

## 45.1 Retrieved content is untrusted

Papers, web pages, README files, notebooks, and repository text can contain prompt-injection-like instructions.

Research tools must wrap retrieved content as **data**. Instructions inside sources cannot alter:

- system policy;
- budgets;
- approval classes;
- allowed tools;
- challenge rules;
- secret access.

## 45.2 External code is untrusted

Before executing code from a repository:

1. fetch/read;
2. static inspect;
3. identify dependencies/network/file writes;
4. sandbox;
5. only then adapt or execute.

## 45.3 Dependency supply chain

Execution environments should:

- lock dependencies;
- prefer known package indexes;
- record package versions/hashes where feasible;
- disallow arbitrary installation scripts under strict mode;
- preserve environment manifests for promoted versions.

## 45.4 Filesystem boundaries

Tools must honor a project root plus explicit artifact/cache locations. Attempts to read unrelated private directories require additional permission.

---

# 46. Reproducibility

A promoted result must be reproducible from its artifact manifest.

Each run records:

```text
git commit / working-tree patch hash
source hash
data hashes
dependency lock
environment image
provider
hardware
random seeds
command
config
validation protocol
metric implementation version
```

`ml-stack reproduce v4` should reconstruct the run as closely as provider availability allows.

If exact hardware is unavailable, the report must say the reproduction is approximate.

---

# 47. Determinism

When a challenge requires deterministic execution:

- set framework seeds;
- configure deterministic kernels where practical;
- control thread counts if needed;
- pin library versions;
- avoid runtime hardware-dependent branches;
- verify repeated inference output;
- static scan for time/random/environment-dependent behavior.

If perfect determinism is impossible, ML-Stack must surface the reason instead of pretending.

---

# 48. Deliverable generator and submission adapter

The Deliverable Generator is requirements-driven. A competition submission is one supported deliverable type, not the universal output.

It reads:

- `requirements.md`;
- requirements lock;
- challenge/platform lock when present;
- promoted artifact bundle;
- requested export map.

Generic deliverable checks include:

```text
required path exists
format is correct
entry point is executable when required
runtime arguments match the contract
artifact hashes recorded
no unexpected files when a strict package is required
offline/network policy satisfied
determinism policy satisfied
resource policy satisfied
```

When a deliverable is a prediction/submission file, the submission adapter additionally checks:

```text
ID equality
row count
column equality
ordering
dtype
serialization
value domain
JSON/string encoding
list lengths
NaN/inf
duplicate IDs
```

When a deliverable is a model package, the model-package adapter can check:

```text
loadability
checkpoint/config/tokenizer consistency
inference smoke test
declared framework/version
size/runtime bounds
license/metadata requirements
```

When a deliverable is a benchmark/report, the report adapter checks required metrics, tables, citations, and reproducibility commands.

Checksums and an audit summary are attached to every exported artifact set.

---

# 49. Challenge score ingestion

External challenge feedback is a distinct evidence class.

Example:

```yaml
external_score:
  source: leaderboard
  version: v5
  score: 0.7132
  metric: challenge_public
  observed_at: ...
  split: unknown
```

The research loop may learn from external scores if challenge rules permit repeated submissions, but:

- external feedback is never relabeled as CV;
- public leaderboard overfitting risk is tracked;
- submission budgets are respected;
- hidden answers are never requested.

---

# 50. Experiment-report format

For each experiment:

```markdown
# EXP-0041

Hypothesis:
Parent:
Change:
Evidence:
Validation protocol:
Compute:
Runtime:
Status:

## Result
Metric:
Delta vs parent:
Fold scores:
Uncertainty:

## Diagnostics
...

## Decision
PROMOTE / REJECT / INCONCLUSIVE

## Reason
...
```

The final report synthesizes experiments rather than dumping raw logs.

---

# 51. Stopping policy

Autonomous experimentation stops when any configured condition is met:

- target score reached with required robustness;
- wall-clock budget reached;
- cost budget reached;
- experiment budget reached;
- no viable hypotheses remain above value threshold;
- provider capacity unavailable beyond retry window;
- fatal ambiguity/rule issue needs user input;
- user stops the run.

Before stopping due to budget, ML-Stack should preserve the best valid version and generate a report.

---

# 52. Failure taxonomy

Failures are classified:

```text
CODE_ERROR
DEPENDENCY_ERROR
DATA_ERROR
OOM
TIMEOUT
PROVIDER_TRANSIENT
PROVIDER_QUOTA
AUTH
NETWORK
METRIC_ERROR
INVALID_PREDICTION
LEAKAGE
RULE_VIOLATION
NONDETERMINISM
RESEARCH_DEAD_END
DOOM_LOOP
BUDGET_EXHAUSTED
USER_INTERRUPT
UNKNOWN
```

The class determines retry behavior.

No failure should disappear into plain text only.

---

# 53. Heartbeats and orphan jobs

For remote work:

- track provider job ID;
- record last status retrieval;
- separate control-plane connectivity from execution status;
- mark uncertain jobs `ORPHANED`, not `FAILED`;
- reconcile them on resume.

Long-running jobs should use provider-side persistence, not require the user's laptop to stay awake.

---

# 54. Notifications and walk-away operation

The user should be able to leave after `/ml-stack`.

Default notifications:

- "Baseline complete: v1, measured CV X"
- "Paid compute approval required: estimated Y"
- "Target reached: vN, measured CV X"
- "Blocked by fatal rule ambiguity"
- "Final submission ready"

Do not notify for every fold or ordinary failed hypothesis.

---

# 55. Observability

Local status:

```text
/ml-stack status
```

Example:

```text
Challenge: Vessel Re-ID
State: EXPERIMENT_LOOP
Best: v4
Metric: 0.5841 ± 0.0062 (locked grouped CV)
Target: 0.60
Experiments: 14 complete / 3 running / 5 queued
Compute:
  local: 7 runs
  kaggle: 4 runs
  hf_jobs: 6 runs
Budget:
  wall: 2h14m / 6h
  GPU: 1.7h / 4h
  paid compute: $0.00 / $0.00
Current:
  H-021 metric-learning margin sweep
  H-024 multimodal feature fusion
```

This is a view over state, not a second UI framework.

---

# 56. Installation targets and portability contract

A feature belongs in one of three layers:

### Layer A — Canonical skill behavior

Portable prose/workflow.

### Layer B — Common MCP/runtime

Portable action schema.

### Layer C — Host glue

Only:

- file locations;
- plugin manifest;
- command namespace;
- host hooks;
- permission declarations;
- UI rendering hints.

No scientific logic should live only in Layer C.

---

# 57. Optional remote `ml-stackd`

A small remote daemon is needed for environments that cannot reach a local MCP process.

Responsibilities:

- authenticated MCP endpoint;
- session/event API;
- remote job orchestration;
- webhook receiver;
- credential references;
- artifact metadata.

It does **not** need a chat UI.

Deployment options can include a user-owned VM/container/serverless target. ML-Stack should not require one when the host supports local tools.

---

# 58. API stability

Public interfaces:

```text
MCP tool names/schemas
config schema
ledger migration format
artifact manifest
provider interface
host adapter generator interface
```

Use semantic versioning.

Breaking tool-schema changes require an adapter compatibility layer for at least one major version where practical.

---

# 59. Testing strategy

## 59.1 Unit tests

Cover:

- challenge parser;
- metric logic;
- split logic;
- leakage detectors;
- experiment comparison;
- budget accounting;
- secret redaction;
- artifact hashing;
- version promotion;
- state transitions.

## 59.2 Provider contract tests

Every provider passes the same fake workload:

```text
capabilities
submit
status
logs
artifact
cancel
failure
timeout
```

Scheduler features are tested only for providers claiming scheduler support.

## 59.3 Integration challenge fixture

Ship tiny synthetic fixtures for:

- tabular classification;
- text classification;
- image classification;
- structured custom-output challenge.

CI should run `/ml-stack baseline` end-to-end.

## 59.4 Replay tests

Recorded event streams should replay into the same state.

## 59.5 Fault injection

Test:

- kill control plane during remote training;
- network disconnect;
- provider 500;
- quota exhausted;
- OOM;
- corrupted artifact;
- missing submission rows;
- duplicate IDs;
- context compaction during active experiment;
- repeated identical tool calls.

## 59.6 Host smoke tests

For each supported host, verify:

- skill discovery;
- invocation;
- MCP availability;
- read/write permission behavior;
- uninstall cleanliness.

---

# 60. CI

Recommended CI gates:

```text
lint
format
typecheck
unit
provider-contract-fakes
integration-small
skill-render
host-adapter-render
schema compatibility
security static checks
parity scan
license/notice check
```

The parity scan should fail when the pinned/upgraded ML Intern surface changes without an explicit mapping decision.

---

# 61. Acceptance criteria for v1.0

ML-Stack v1.0 is not "done" until all of the following hold:

1. `./setup` installs successfully for at least Claude Code, Codex, and OpenCode.
2. A generic MCP install path exists.
3. The ChatGPT package/remote-MCP path is documented and testable for eligible environments.
4. `/ml-stack` can ingest a sample challenge without manual file mapping.
5. It creates and locks a validation protocol.
6. It runs a valid baseline, promotes `v1`, and materializes whatever deliverables the active requirements contract requests.
7. It launches at least one remote CPU or GPU experiment through the provider interface.
8. It can resume after the orchestrator is killed.
9. It can run multiple independent experiments concurrently.
10. It can reject a worse result without promoting it.
11. It can promote a better result to `v2`.
12. It can paper-search, traverse citations, read sections, and extract an evidence-backed recipe.
13. It can search documentation and working GitHub examples.
14. It can inspect an HF dataset and validate SFT/DPO/GRPO schemas.
15. It performs a submission schema audit.
16. It performs a held-out-answer/leakage audit.
17. It preserves measured-vs-estimated-vs-hypothesis labels.
18. It enforces configured compute and LLM budgets.
19. It emits durable events and experiment ledger records.
20. It includes an explicit parity report covering every tracked ML Intern feature at the pinned snapshot.
21. It can notify on approval/final completion.
22. It produces `ml-stack-report.md`.
23. It does not require an ML-Stack-specific chat frontend.

---

# 62. Implementation phases

## Phase 0 — Repository + installer skeleton

Deliver:

- canonical source layout;
- `./setup`;
- CLI skeleton;
- shared skill generator;
- MCP skeleton;
- config loader;
- SQLite ledger;
- host detection.

Exit criterion: `/ml-stack doctor` works.

## Phase 1 — Local challenge loop

Deliver:

- requirements capture/compiler;
- visible `exp/`, `research/`, `bench/`, and `notes/` workspace;
- discovery;
- challenge/project parser;
- data profiler;
- validation lock;
- local baseline execution;
- evaluator;
- generic deliverable audit plus submission adapter;
- versioning.

Exit criterion: tiny challenge -> valid `v1` completely unattended.

## Phase 2 — Research parity

Deliver:

- paper service with all required operations;
- docs search/fetch;
- OpenAPI search;
- web search and optional browser adapter;
- URL/page capture with source notes;
- GitHub example/repo/file tools;
- HF dataset inspector;
- isolated research workers;
- evidence store;
- automatic paper/doc/web/code notes;
- research synthesis.

Exit criterion: research package yields testable recipes with citations/provenance.

## Phase 3 — Compute broker

Deliver:

- local provider;
- HF Jobs;
- HF sandbox;
- Kaggle;
- Modal;
- generic SSH/Slurm interface;
- capability/quota/estimate;
- run supervisor;
- artifacts;
- retries;
- heartbeat/resume.

Exit criterion: same experiment spec runs on two different remote providers without workflow changes.

## Phase 4 — Autonomous experiment engine

Deliver:

- hypothesis queue;
- multi-fidelity execution;
- comparison/promotion gate;
- parallelism;
- experiment search;
- robustness checks;
- target/budget stopping;
- automatic `exp/*` experiment notebooks;
- model/hardware/provider benchmarks;
- post-run lesson extraction into project memory.

Exit criterion: baseline -> multiple experiments -> automatically promoted `v2+`, with the experiment history and lessons written to human-readable files.

## Phase 5 — Full host packaging

Deliver:

- Claude Code native plugin;
- Codex skill/plugin adapter;
- ChatGPT plugin/app + remote MCP packaging;
- OpenCode adapter;
- generic digest.

Exit criterion: canonical workflow behaves equivalently across hosts.

## Phase 6 — ML Intern parity hardening

Deliver:

- all P0/P1 parity rows;
- session tags;
- remote trace sinks;
- HF repo lifecycle tools;
- scheduling;
- notifications;
- Trackio;
- model/effort probes;
- parity scanner.

Exit criterion: parity CI green at pinned upstream snapshot.

---

# 63. Recommended implementation stack

These are defaults, not architectural requirements.

```text
Language: Python 3.12+
Environment/package manager: uv
Schemas/config: Pydantic
MCP: FastMCP or equivalent stable MCP SDK
Async: asyncio
Ledger: SQLite
Data frames: pandas/polars as task-dependent
HTTP: httpx
CLI: Typer/Rich or minimal equivalent
Serialization: JSON/YAML/TOML
Testing: pytest
```

Why Python:

- ML ecosystem compatibility;
- easy provider SDK integration;
- direct experiment-template reuse;
- simpler data inspection;
- fastest path to parity with ML Intern's ML-specific capabilities.

Performance-critical pieces can later use Rust/native binaries without changing public schemas.

---

# 64. Design of the canonical `/ml-stack` Skill

The skill should be concise enough for host skill systems. Deep detail lives in references.

Primary SKILL.md responsibilities:

1. identify whether current request is a full challenge run or focused subcommand;
2. initialize/resume ML-Stack state;
3. call challenge ingest;
4. obey the state machine;
5. delegate research to isolated workers;
6. use tools rather than manually simulating results;
7. never claim unmeasured scores;
8. respect budgets/approvals;
9. finish with exact artifact links/paths.

Supporting references:

```text
references/scientific-method.md
references/validation.md
references/research.md
references/compute-routing.md
references/challenge-compliance.md
references/versioning.md
```

This avoids a monolithic prompt.

---

# 65. Research worker prompt contract

Research workers should be instructed to:

- start with papers;
- crawl downstream citations;
- read method/experiments/results sections;
- connect recipe to measured result;
- verify current implementation APIs;
- find working code;
- verify dataset format;
- rank recipes by evidence and feasibility;
- state gaps;
- return concise structured results;
- never mutate project files;
- never launch compute.

This mirrors the strongest part of ML Intern while making it reusable as a plugin specialist.

---

# 66. Experimenter prompt contract

The experimenter must:

- receive one hypothesis and locked validation reference;
- make the minimum code/config changes;
- create an isolated run directory/branch;
- pass static/smoke checks;
- submit through compute broker;
- record provider ID;
- collect outputs;
- never promote its own result;
- never modify the validation protocol.

---

# 67. Skeptic prompt contract

The skeptic sees:

- baseline;
- candidate;
- metrics/fold results;
- change diff;
- logs;
- relevant evidence.

It checks:

```text
Could this gain be leakage?
Was the split changed?
Was a fold dropped?
Was compute/training length different in a confounding way?
Is the metric implementation the same?
Is this likely seed noise?
Did a bug accidentally use test data?
Does the result violate the challenge?
```

The Result Judge makes the final structured decision.

---

# 68. No fabricated progress

A core policy:

```text
Do not say "training is running" unless a provider/local process ID exists.
Do not say "score improved" unless the evaluator emitted a result.
Do not say "submission is valid" unless the submission auditor passed.
Do not say "paper says X" unless evidence retrieval supports it.
Do not say "free compute available" unless quota/capability was checked.
```

This policy should exist in both canonical skill instructions and runtime assertions where possible.

---

# 69. Provenance graph

Evidence and experiments form a graph:

```text
Paper E12 ─┐
Docs E14 ──┼─> Hypothesis H7 -> Experiment EXP9 -> Run R19 -> Metric M19
Code E15 ──┘                                         |
                                                      v
                                                Version v3
```

The final report can answer:

- Why is v3 different from v2?
- What evidence led to this change?
- Which run measured the gain?
- What would we try next?

---

# 70. Resource-aware research-to-experiment conversion

The best paper method may be infeasible.

Recipe ranking should account for:

```text
reported quality
transfer relevance
implementation maturity
dataset compatibility
GPU VRAM
training duration
license
challenge rules
available quota
inference constraints
```

A lower-paper-score recipe can rank first if it is the strongest feasible choice.

---

# 71. Handling tiny/tabular CPU challenges

ML-Stack must not over-route everything to GPUs.

For small CPU challenges it should emphasize:

- leakage-safe validation;
- feature engineering;
- strong gradient boosting;
- linear/nearest-neighbor baselines;
- calibrated ensembles;
- efficient CV;
- exact structured decoding where task-appropriate and rules permit.

The compute broker should keep these local or on cheap CPU unless runtime profiling justifies remote execution.

---

# 72. Handling GPU-heavy challenges

For deep-learning tasks:

1. use local/small CPU for parsing and sampling;
2. run a tiny local/cheap GPU smoke test;
3. estimate memory;
4. route to right GPU;
5. checkpoint;
6. parallelize only independent experiments;
7. retrieve compact metrics first;
8. retrieve heavy checkpoints only for promoted candidates unless needed.

---

# 73. Model and artifact caching

Avoid paying repeatedly for:

- tokenizer downloads;
- pretrained weights;
- transformed datasets;
- embeddings;
- feature matrices;
- compiled kernels.

Cache keys must include relevant config/data/model hashes. Cache reuse can never cross incompatible preprocessing or data permissions silently.

---

# 74. Branch/worktree isolation

For coding-agent hosts, experiments should use isolated worktrees or generated run directories to permit parallel work.

Recommended:

```text
main workspace -> promoted version
.ml-stack/worktrees/EXP-001
.ml-stack/worktrees/EXP-002
```

Each experiment diff can be reviewed and promoted without race conditions.

Provider jobs receive a frozen source bundle/hash.

---

# 75. Concurrency control

Locks:

```text
challenge-spec lock
validation-protocol lock
version-promotion lock
artifact-write lock
provider quota semaphore
GPU budget semaphore
```

Experiments may run concurrently, but only one promotion transaction can create a given next version.

---

# 76. Comparison across protocol changes

If validation must change:

```text
val_v1 -> val_v2
```

ML-Stack runs a bridge:

```text
current best config on val_v1
current best config on val_v2
```

Historical scores remain under their original protocol. The report must not present them as one continuous scale.

---

# 77. Ensembling

Ensembling is an explicit experiment family.

Requirements:

- base model OOF predictions available;
- no test-label tuning;
- weights selected on locked validation;
- marginal complexity/cost recorded;
- compare against best single model.

Simple averaging/blending should be tested before complex stacking.

---

# 78. Advanced optimization

P1/P2 features:

- automatic feature-group ablations;
- error clustering;
- slice discovery;
- disagreement analysis across models;
- calibration diagnostics;
- learning curves;
- data scaling curves;
- active external-data candidate search when rules allow;
- pseudo-label experiments with strict provenance;
- test-time augmentation;
- distillation;
- constrained ensemble search.

All are ordinary hypotheses under the same ledger.

---

# 79. Human checkpoints

Even in autonomous mode, optional checkpoints can be configured:

```text
after challenge lock
before paid GPU
before external dataset use
before pushing to a remote repo
before final submission
```

The user can set:

```toml
[approvals]
challenge_lock = false
paid_compute = true
external_data = true
remote_publish = true
final_submission = false
```

---

# 80. Remote publication

ML-Stack can prepare but should not automatically publish artifacts publicly unless allowed.

Publication destinations:

- GitHub branch/PR;
- HF model/dataset/Space repo;
- generic artifact store.

Public visibility is an approval-class action.

---

# 81. Trace sharing

Local traces are private by default.

Commands:

```text
/ml-stack trace export
/ml-stack trace share private
/ml-stack trace share public
```

Remote trace upload is opt-in/configurable. Secret redaction runs before export.

This preserves ML Intern's useful trace-sharing behavior without making a specific HF dataset repository mandatory.

---

# 82. Licensing and upstream inspiration

ML-Stack should be an independent implementation informed by public behavior and architecture.

At the pinned research snapshot:

- `huggingface/ml-intern` is distributed under Apache-2.0.
- `garrytan/gstack` is distributed under MIT.

If code is copied/adapted rather than independently reimplemented, all applicable license, notice, and attribution requirements must be followed.

The safest default is:

- adopt ideas, interfaces, and workflow concepts;
- write ML-Stack's own generalized implementation;
- preserve required notices for any directly reused code.

---

# 83. Research basis for this specification

This spec was designed after inspecting the current public surfaces of:

## Hugging Face ML Intern

Repository:

```text
huggingface/ml-intern
```

Pinned snapshot for this parity contract:

```text
b0d6752723d17ef2ea7a54f5aeb63abebba99e47
```

Inspected areas include:

```text
README.md
AGENTS.md
agent/core/
agent/context_manager/
agent/tools/
agent/sft/
backend/
tests/
```

Important current tool/runtime surfaces inspected include:

```text
agent/core/tools.py
agent/tools/papers_tool.py
agent/tools/research_tool.py
agent/tools/dataset_tools.py
agent/tools/docs_tools.py
agent/tools/jobs_tool.py
agent/tools/sandbox_tool.py
agent/tools/hf_repo_files_tool.py
agent/tools/hf_repo_git_tool.py
agent/tools/github_find_examples.py
agent/tools/github_list_repos.py
agent/tools/github_read_file.py
agent/tools/web_search_tool.py
agent/tools/plan_tool.py
agent/tools/notify_tool.py
agent/sft/tagger.py
```

## gstack

Repository:

```text
garrytan/gstack
```

The relevant inspiration is its packaging/distribution model:

- one repository;
- setup installer;
- many specialist Skills;
- multi-host installation;
- project/team mode;
- host-specific generated adapters;
- instruction-only fallback for agents that can read rules but cannot install full plugins.

ML-Stack does **not** copy gstack's product-development roles. It applies the same portable-specialist packaging idea to autonomous ML research.

## Host ecosystems

The architecture also accounts for current official plugin/skill/MCP patterns in:

- OpenAI ChatGPT/Codex;
- Claude Code;
- OpenCode;
- generic Agent Skills / MCP hosts.

Because host APIs evolve, ML-Stack's adapter layer and `doctor` command must detect actual capabilities rather than assuming a fixed product surface.

---

# 84. Key product invariant

A user should never have to think:

> "Should I open ML-Stack instead of my agent?"

There is no separate place to go.

They should think:

> "I am already in Codex / Claude Code / ChatGPT / OpenCode. I need serious ML work. Run `/ml-stack`."

That is the product.

---

# 85. Canonical end-to-end example

User has placed a `requirements.md` in the project. It requires:

```text
- strongest leakage-free model possible
- train-only validation
- GPU training
- final files:
    solution_v1.py
    submission.csv
```

The user runs:

```text
/ml-stack target=0.60 wall_time=4h compute=free-first
```

ML-Stack:

```text
1. Snapshots requirements.md verbatim and compiles requirements lock r1.
2. Detects challenge statement, train/test/sample submission.
3. Parses task as cross-modal re-identification.
4. Extracts grouping rule and metric.
5. Profiles assets and finds entity/group leakage risk.
6. Locks group-aware validation.
7. Writes baseline experiment to exp/0001-baseline/.
8. Produces internal promoted bundle v1.
   Measured CV: 0.47
9. Research workers inspect recent re-ID papers, citation graphs,
   metric-learning recipes, documentation, and implementation examples.
10. Writes source-linked notes to research/ and reusable findings to notes/.
11. Creates hypotheses:
      H1 stronger augmentation
      H2 metric learning loss
      H3 cross-modal fusion
      H4 image-size normalization
      H5 cluster assembly change
12. Runs independent experiments under exp/0002..., exp/0003..., exp/0004....
13. H1 = 0.49 -> promote v2.
14. H2 = crash/OOM -> record failure, learn memory signature, resubmit equivalent lower-batch config.
15. H4 = 0.48 -> reject.
16. H2 retry = 0.54 -> promote v3.
17. Error analysis + paper evidence suggests H6.
18. H6 = 0.59 but seed variance high -> robustness required.
19. Robust result = 0.582 ± 0.007 -> promote v4.
20. H3 = 0.607 -> target reached -> promote v5.
21. Retrains the selected final configuration under the requirements contract.
22. Exports v5 to the user-required names:
      solution_v1.py
      submission.csv
23. Runs schema/compliance/determinism/runtime checks.
24. Updates bench/, notes/, and the cross-project learning store.
25. Writes ml-stack-report.md.
26. Sends "Final ready: v5, measured CV 0.607."
```

If a different `requirements.md` requests `train.py`, `model.pt`, and `report.json`, the same workflow exports those instead. Internal versions remain `v1...vN`.

At no point does ML-Stack claim 0.60+ before the evaluator proves it.

---

# 86. Initial milestone definition

The first engineering milestone should **not** attempt every provider or advanced optimizer.

Build this vertical slice first:

```text
./setup
   ->
/ml-stack on a local CSV challenge
   ->
challenge lock
   ->
data profile
   ->
validation lock
   ->
paper/doc/GitHub research
   ->
baseline v1
   ->
three hypothesis experiments
   ->
promote winner to v2
   ->
deliverable audit
   ->
report
```

Then add remote compute without changing the workflow contract.

This validates the architecture before provider complexity expands.

---

# 87. Decision log: choices locked by this spec

1. **Name:** ML-Stack.
2. **Shape:** plugin suite, not standalone chat product.
3. **Primary UX:** `/ml-stack`.
4. **Host remains primary agent/brain.**
5. **One canonical workflow source, generated host adapters.**
6. **MCP/tool server for durable actions.**
7. **Python-first core.**
8. **SQLite event/experiment ledger.**
9. **Paper-first independent research subagents.**
10. **Provider-neutral compute broker.**
11. **Local + HF + Kaggle + Modal as initial practical provider family.**
12. **Immutable internal versions `vN`; exported filenames are entirely requirements-driven.**
13. **Validation locks before broad experimentation.**
14. **Measured claims only.**
15. **Budget-bounded autonomy.**
16. **No custom frontend required.**
17. **ML Intern parity is pinned and machine-audited.**
18. **gstack inspiration is packaging/host portability, not domain logic.**

---

# 88. Definition of success

ML-Stack succeeds when a user can install it once, enter an unfamiliar ML project or challenge folder in their preferred agent, provide or generate `requirements.md`, type `/ml-stack`, leave, and later return to the exact requested deliverables plus a set of reproducible internal versions whose improvement path is supported by real experiments and research evidence.

The product is not judged by how many tools it exposes.

It is judged by whether it repeatedly converts:

```text
unknown challenge
        +
available data
        +
current literature
        +
available compute
        +
bounded budget
```

into:

```text
the strongest valid solution ML-Stack could actually demonstrate,
with deliverables that pass their active requirements contract, a provenance trail that can be audited,
and no fabricated confidence.
```

That is the architecture contract for ML-Stack.

---

# 89. Requirements as a first-class artifact

## 89.1 The user's words are the source of truth

ML-Stack must persist the user's exact project requirements as Markdown before doing substantive work.

The preferred visible file is:

```text
requirements.md
```

If requirements arrive only through chat, `/ml-stack` writes them to `requirements.md` or, if the user does not want the root modified, to:

```text
.ml-stack/requirements/user.md
```

The raw Markdown is never silently rewritten. A machine-readable lock is derived from it:

```text
.ml-stack/requirements/lock.yaml
```

The lock contains provenance back to the exact Markdown headings/lines that produced each constraint.

## 89.2 Discovery precedence

Requirements are discovered in this order:

```text
1. explicit --requirements <path>
2. requirements content supplied in the invoking user message
3. ./requirements.md
4. ./ML_STACK_REQUIREMENTS.md
5. platform/challenge rules and statement files
6. project README / AGENTS.md / relevant docs
7. ML-Stack defaults for unspecified fields only
```

User/project requirements may be stricter than platform rules. They may not authorize behavior explicitly prohibited by higher-authority platform/challenge rules.

## 89.3 Requirements compiler

The Markdown compiler extracts:

```yaml
objective:
success_criteria:
mode:
  challenge: true|false
  benchmark: true|false
  research: true|false
inputs: []
target:
metric:
validation:
deliverables: []
runtime:
entrypoints: []
compute:
  cpu:
  gpu:
  accelerator_required:
  memory:
  timeout:
network:
  development:
  training:
  inference:
external_data:
pretrained_models:
allowed_methods: []
prohibited_methods: []
test_isolation:
determinism:
experimentation:
research:
benchmarking:
reporting:
comments_style:
submission:
approval:
stop_conditions:
special_constraints: []
```

Every compiled field has one of:

```text
explicit_user
explicit_platform
inferred
default
unknown
```

## 89.4 Conflict handling

Conflicts are not resolved by silently picking a convenient interpretation.

The compiler records:

```yaml
conflicts:
  - left: "GPU training mandatory"
    right: "pure CPU solution"
    severity: fatal
    sources: [...]
```

If both rules apply to the same run and cannot be reconciled, ML-Stack asks once or stops with a clear conflict report.

This matters because different projects can legitimately require completely different execution profiles: one may require strict CUDA-only training and inference, while another may explicitly require a pure CPU final pipeline.

## 89.5 Requirements revisions

Changes are stored as:

```text
requirements.md                  current human file
.ml-stack/requirements/r1.md     immutable snapshot
.ml-stack/requirements/r2.md
.ml-stack/requirements/r3.md
```

Every experiment and version records its requirements revision.

## 89.6 Deliverable contract

There is no built-in assumption that a task must produce `solution.py`.

The contract can request any combination of:

```text
source files
Python packages
CLI entry points
prediction files
checkpoints
safetensors
ONNX/TorchScript
notebooks
Dockerfiles
model cards
datasets
benchmark JSON
plots
reports
documentation
Git branches/PRs
HF model/dataset/Space artifacts
archives
custom files
```

The requirements lock declares:

```yaml
deliverables:
  - path: solution_v1.py
    required: true
    checks:
      - python_compile
      - no_comments
      - cli_signature
  - path: submission.csv
    required: true
    checks:
      - sample_schema
      - ids_exact
```

or any other required structure.

---

# 90. Default autonomous ML lab workspace

Without project-specific overrides, ML-Stack creates four visible working surfaces:

```text
exp/
research/
bench/
notes/
```

These are not caches. They are the inspectable scientific record.

## 90.1 `exp/*` experiments

Every real experiment gets a directory:

```text
exp/0001-baseline/
exp/0002-char-cnn/
exp/0003-gru/
exp/0004-loss-ablation/
...
```

Each directory SHOULD contain:

```text
hypothesis.md
config.yaml
run.md
metrics.json
notes.md
stdout.log or a remote-log pointer
artifacts/
```

`hypothesis.md` states before execution:

```text
what changes
why it might work
what evidence supports it
what is held constant
promotion criterion
expected resource cost
```

`run.md` records:

```text
status
provider
hardware
command
start/end time
source hash
data hash
requirements revision
validation revision
parent version
```

`notes.md` records interpretation after the run.

The global experiment index is written to both:

```text
exp/index.md
.ml-stack/ledger.sqlite
```

The Markdown index is for humans/agents. SQLite is for exact querying.

## 90.2 Reusable experiment templates

The plugin exposes Skills such as:

```text
/ml-stack experiment baseline
/ml-stack experiment ablation
/ml-stack experiment hparam
/ml-stack experiment seed
/ml-stack experiment ensemble
/ml-stack experiment scale
/ml-stack experiment reproduce
```

Templates only structure the scientific method; they do not prescribe a model family.

---

# 91. Web, browser, documentation, and source-learning features

ML-Stack should be able to research like an ML engineer rather than merely call one search endpoint.

## 91.1 Research surfaces

The research plane supports:

```text
web search
page fetch/read
host browser, when available
arXiv
Semantic Scholar
Hugging Face Papers
citation graphs
paper section reading
paper full-text snippet search
paper recommendations
official documentation
OpenAPI specs
GitHub repos/files/examples/issues/PRs
model cards
dataset cards
benchmark pages
release notes/changelogs
```

## 91.2 Source notebook

Every useful source is registered in `research/evidence.jsonl` and summarized in the appropriate Markdown notebook:

```text
research/papers.md
research/web.md
research/docs.md
research/code.md
research/datasets.md
```

A note includes:

```text
source
retrieval date
claim
relevance
confidence
what experiment it motivates
whether the finding was reproduced locally
```

## 91.3 Browser capability

When the host offers a real browser/computer-use tool, ML-Stack may use it for:

```text
documentation navigation
interactive benchmark dashboards
pages requiring normal browser rendering
download links explicitly permitted by requirements
visual inspection of public charts/tables
```

The browser is a research tool, never a route around project restrictions.

## 91.4 Changelog awareness

Before implementing against fast-moving libraries, ML-Stack checks current official docs/release notes rather than assuming an old API is still valid.

## 91.5 Source trust hierarchy

Default technical source preference:

```text
official paper / primary benchmark
official documentation
official framework examples
maintainer repository
reputable reproduced implementation
secondary tutorial
forum/social discussion
```

Community discussion can generate hypotheses but cannot by itself become a high-confidence technical claim.

---

# 92. Benchmarking as a first-class subsystem

ML-Stack benchmarks both **model quality** and **systems behavior**.

## 92.1 Model benchmark records

For every promoted or serious candidate, record when applicable:

```text
primary metric
secondary metrics
train score
validation score
per-class/per-slice metrics
seed mean/std
calibration
model size
parameter count
checkpoint size
training time
inference throughput
latency
peak RAM
peak VRAM
CPU/GPU utilization
```

## 92.2 Hardware benchmark records

`bench/hardware.md` and `bench/runtime.jsonl` accumulate empirical measurements for:

```text
CPU model
GPU model
VRAM/RAM
framework
dtype
batch size
input shape
tokens/sec or samples/sec
peak memory
compile/startup time
```

This makes future resource estimates calibrated by actual runs rather than generic guesses.

## 92.3 Provider benchmarks

`bench/providers.md` tracks:

```text
provider
hardware flavor
queue delay
startup latency
run reliability
preemption/failure rate
effective cost
artifact transfer speed
quota observations
```

The compute broker may use these observations for future routing.

## 92.4 Benchmark Skills

Expose:

```text
/ml-stack benchmark model
/ml-stack benchmark hardware
/ml-stack benchmark provider
/ml-stack benchmark compare
/ml-stack benchmark regression
```

## 92.5 Regression benchmarks

A promoted version can register a benchmark baseline. Later code changes run a compact regression suite and flag:

```text
metric regression
runtime regression
memory regression
determinism regression
artifact-size regression
```

---

# 93. Notes and scientific notebook system

ML-Stack automatically keeps concise Markdown notes.

Default files:

```text
notes/task.md
notes/data.md
notes/validation.md
notes/decisions.md
notes/failures.md
notes/ideas.md
notes/final.md
```

Rules:

- notes summarize evidence; they do not replace raw logs;
- every important decision links to experiments/evidence;
- failed ideas remain recorded;
- contradictory findings are preserved;
- stale notes can be superseded but not silently erased;
- agents should read relevant notes before repeating work.

`/ml-stack notes` shows or updates the project notebook.

At the end of a run, `notes/final.md` should contain the compact state a fresh agent needs to continue immediately.

---

# 94. Cross-project learning: ML-Stack gets better as it trains more models

ML-Stack should accumulate **scientific memory**, not hidden-answer memory.

## 94.1 Three memory scopes

```text
Project memory:
  ./notes/
  ./exp/
  ./research/
  ./bench/
  ./.ml-stack/ledger.sqlite

Workspace/team memory:
  configurable shared ML-Stack knowledge store

User-global memory:
  ~/.ml-stack/knowledge/
```

Global learning is opt-in/configurable in environments where persistent storage is undesirable.

## 94.2 What it learns

Reusable knowledge objects include:

```text
task archetypes
dataset-shape patterns
validation strategies that worked
leakage failure patterns
representation/model recipe cards
hyperparameter priors
successful ablations
failed ablations
optimizer/scheduler behavior
runtime scaling laws
VRAM/RAM estimates
hardware throughput
provider reliability
dependency/API pitfalls
OOM signatures and fixes
numerical-instability signatures
paper-to-code mappings
implementation patterns
ensemble complementarity patterns
```

## 94.3 What it must not learn globally

Never promote these into cross-project memory:

```text
test predictions
hidden labels
private held-out answers
row-specific rules
challenge-specific IDs as target proxies
secret credentials
private raw datasets without explicit permission
prohibited metadata shortcuts
copyrighted paper bodies
```

## 94.4 Knowledge card schema

```yaml
knowledge_id: K-00142
kind: recipe|failure|validation|hardware|provider|api|paper
scope: project|workspace|global
claim: ...
conditions:
  task_family: ...
  dataset_scale: ...
  modality: ...
evidence:
  projects: 3
  experiments: [EXP-...]
  papers: [E-...]
confidence: 0.82
last_verified: ...
expires_or_review_after: ...
anti_conditions: []
```

## 94.5 Promotion policy

A project observation does not automatically become universal knowledge.

Promotion sequence:

```text
single run -> project note
repeated seeds/folds -> project lesson
same pattern across multiple experiments -> candidate reusable lesson
same pattern across multiple projects or strong literature support -> global knowledge card
```

The system records counterexamples and can lower confidence.

## 94.6 Retrieval

At project start, ML-Stack retrieves relevant prior cards based on:

```text
task family
modality
dataset size
target type
metric
constraints
hardware
framework
input statistics
```

Retrieved knowledge creates **hypotheses and priors**, never unquestioned final choices.

## 94.7 Forgetting and staleness

Library/API/provider facts decay faster than mathematical/modeling lessons.

Knowledge objects have:

```text
last_verified
source versions
confidence
staleness policy
```

Current web/docs can refresh stale operational knowledge.

## 94.8 Memory implementation

P0:

```text
SQLite + FTS
structured YAML/JSON knowledge cards
```

P1:

```text
optional local embeddings / semantic retrieval
```

The memory layer must work offline using previously stored knowledge.

---

# 95. Expanded ML Intern parity contract: no functional surface left behind

The earlier parity table remains valid, but v1.0 parity must cover the **entire functional repository surface** of the pinned ML Intern snapshot, not only its headline tools.

Implementation priority labels are sequencing labels, not permission to omit a feature.

## 95.1 Runtime and agent-loop parity

Required equivalents include:

```text
streaming and non-streaming LLM calls
tool call routing
malformed tool-argument recovery
dangling tool-call recovery
no-tool continuation guard
LLM error classification
thinking/reasoning history handling
model capability/model gating
tool state transitions
interrupt handling
approval flow
auto-approval policy
cost estimation
usage accounting
usage threshold approvals
bounded autonomous/yolo budget
heartbeat/progress handling
doom-loop detection including polling loops
context compaction
compaction-loop break guards
prompt caching
secret redaction
```

As a plugin/skill suite, these behaviors live in the common runtime and host adapter rather than requiring ML Intern's CLI.

## 95.2 Model/runtime parity

Required equivalents include:

```text
model IDs/normalization
runtime model switching where the host permits it
reasoning-effort preferences
effort capability probing and graceful fallback
local OpenAI-compatible model endpoints
provider router/catalog discovery
LLM parameter normalization
usage/cost telemetry
inference billing/usage projections where available
```

## 95.3 Access/auth parity

Required equivalents include:

```text
HF token discovery
token propagation to tools/MCP
HF access checks
OAuth for remote/web deployment mode
least-privilege scope handling
auth error reporting
sandbox API authentication
credential redaction
```

## 95.4 Session lifecycle parity

Required equivalents include:

```text
session creation
session persistence
session list/history
session resume
session recovery after process restart
interrupt
new/clear session behavior
session expiration
session reaper/cleanup
session upload/export
personal trace repository
private-by-default trace storage
public/private trace visibility changes
event streaming/SSE equivalent
```

The host UI may render sessions differently, but the underlying functions must exist.

## 95.5 Tool parity

All current ML Intern tool families must have plugin/MCP equivalents:

```text
local bash/read/write/edit
sandbox bash/read/write/edit
dataset inspection
HF docs exploration/fetch
dynamic API/OpenAPI discovery
GitHub example finding
GitHub repository listing
GitHub file reading
HF repo file operations
HF repo branch/tag/PR/repo operations
HF Jobs and schedules
notifications
papers/citations/full-text/resources
plan tracking
independent research subagent
sandbox creation/client/runtime
Trackio seeding
web search
MCP third-party tools
```

## 95.6 Hub artifact parity

Preserve equivalents for:

```text
artifact registration
models
datasets
Spaces
repo metadata
run-created artifact tracking
linking artifacts to sessions/jobs
publishing state
```

## 95.7 Messaging parity

Preserve:

```text
notification request models
gateway abstraction
Slack implementation
status/progress notifications
agent-triggered notifications
dedupe/rate handling
```

and generalize to additional providers.

## 95.8 Data upload parity

ML Intern's backend includes dataset-upload handling. ML-Stack therefore needs a generic staged-input service for remote hosts:

```text
upload local dataset/file bundle
content hashing
size/type validation
temporary staging
authorized remote placement
cleanup
link staged data to project/session
```

This is distinct from model training data logic.

## 95.9 Usage/KPI parity

ML Intern contains usage metrics, usage thresholds, backend usage logic, KPI building, and KPI scheduling. ML-Stack maps this to:

```text
per-session LLM usage
tool usage
compute usage
cost estimates/actuals
user/project quotas
threshold approvals
run counts and outcomes
success/failure rates
research/tool efficiency metrics
scheduled KPI aggregation
local/private analytics by default
optional remote aggregate telemetry
```

The existing `scripts/build_kpis.py` concept becomes a plugin-accessible analytics command:

```text
/ml-stack stats
/ml-stack stats build
/ml-stack stats schedule
```

## 95.10 SFT/trajectory-data parity

Preserve:

```text
trajectory serialization
tool/outcome/GPU/sandbox/feedback/model/turn/cost/task tags
SFT dataset build/export
trace slicing/filtering
```

ML-Stack additionally tags experiments, requirements revisions, providers, task archetypes, and promoted versions.

## 95.11 Backlog-prioritization parity

The pinned ML Intern repository contains an automated backlog-prioritization script. ML-Stack generalizes this idea to scientific backlog prioritization:

```text
rank unresolved hypotheses
rank failed runs worth retrying
rank missing parity items
rank technical debt
rank high-value research questions
```

Expose:

```text
/ml-stack backlog
/ml-stack backlog prioritize
```

The ranker uses expected value, evidence gaps, cost, blockers, and user goals.

## 95.12 Orphan-resource cleanup parity

The pinned repository contains orphan sandbox cleanup tooling. ML-Stack must provide:

```text
detect orphan local processes
detect orphan provider jobs
detect abandoned sandboxes
detect stale staged datasets
detect incomplete artifact uploads
safe cleanup
dry-run cleanup
```

Expose:

```text
/ml-stack cleanup
/ml-stack cleanup --dry-run
```

## 95.13 Host-UI functional parity

ML Intern's frontend includes session navigation, chat/tool-call display, activity status, code display, usage meter, authentication state, YOLO/autonomy controls, error/expiry banners, and research state.

ML-Stack does not need to clone the frontend. The plugin must surface equivalent functionality through host-native UI or commands:

```text
/ml-stack status
/ml-stack sessions
/ml-stack usage
/ml-stack autonomy
/ml-stack research status
/ml-stack jobs
/ml-stack errors
/ml-stack artifacts
```

For hosts that support rich tool cards/status panes, adapters should render these natively.

## 95.14 Parity CI is authoritative

The parity scanner must inventory:

```text
agent/core/*
agent/context_manager/*
agent/messaging/*
agent/prompts/*
agent/sft/*
agent/tools/*
backend/*
scripts/*
documented CLI commands
documented user-facing README features
tests that imply a public/reliability behavior
```

A new upstream functional module/test/command cannot be ignored. It must be classified as:

```text
implemented
host-provided-equivalent
presentation-only-equivalent
not-yet-implemented (CI failure for parity release)
```

There is no permanent "nice to have" bucket for upstream functional parity.

---

# 96. Plugin and Skill packaging model for every capability

ML-Stack is distributed as a **capability pack**. Each major subsystem has both:

1. a Skill describing how an agent should use it; and
2. MCP/plugin tools implementing durable actions.

Canonical Skill set:

```text
ml-stack                  full autonomous run
ml-stack-requirements     capture/compile/audit requirements
ml-stack-inspect          project/data/task inspection
ml-stack-research         paper/web/docs/code research
ml-stack-papers           literature and citation workflows
ml-stack-web              web/browser research
ml-stack-docs             documentation/OpenAPI research
ml-stack-experiment       controlled experiment lifecycle
ml-stack-benchmark        model/hardware/provider benchmarking
ml-stack-evaluate         metric/validation execution
ml-stack-ensemble         ensemble search
ml-stack-audit            leakage/compliance/deliverable audit
ml-stack-compute          resource planning/job dispatch
ml-stack-notes            scientific notebook maintenance
ml-stack-learn            memory extraction/retrieval
ml-stack-status           sessions/jobs/budgets/usage
ml-stack-backlog          prioritize scientific next actions
ml-stack-cleanup          orphan resource cleanup
ml-stack-publish          repo/artifact publication
ml-stack-traces           trajectory/trace export and sharing
```

The full `/ml-stack` Skill composes these. A host can also invoke any subsystem directly.

Tools are not duplicated per Skill. Skills share the common MCP surface.

---

# 97. Default behavior when no requirements file exists

If `/ml-stack` is invoked with no explicit requirements document, it immediately creates a draft `requirements.md` from:

```text
the user's request
project/challenge statement
README/AGENTS instructions
detected files
platform constraints
```

Default assumptions fill only missing fields:

```text
- maximize legitimate validated performance
- use leakage-safe train-only/model-development validation
- preserve strict held-out/test isolation
- create exp/* for experiments
- research papers before expensive modeling where useful
- use web/docs/GitHub during development when available and permitted
- keep final runtime offline if platform rules imply offline scoring
- benchmark quality/runtime/memory
- record docs, paper notes, decisions, and failures
- use measured evidence to promote versions
- learn reusable non-sensitive lessons after runs
- respect budget and approval limits
- audit every requested deliverable
```

The draft is included in the requirements lock with each default clearly labeled `default`, so a user can override it later without hunting through hidden prompts.

The practical product loop becomes:

```text
REQUIREMENTS
   -> RESEARCH
   -> BASELINE
   -> exp/*
   -> BENCHMARK
   -> ANALYZE
   -> LEARN
   -> NEXT HYPOTHESIS
   -> ...
   -> PROMOTED VERSION
   -> REQUESTED DELIVERABLES
   -> AUDIT
   -> NOTES + MEMORY
```

That loop is the heart of ML-Stack.

---

# 98. Naming, namespaces, and compatibility lock

The product is named **ML-Stack**. All new implementation, documentation, packages, state directories, Skills, commands, schemas, and remote services SHALL use the following names unless a host requires a different filesystem convention:

```text
Product                 ML-Stack
Repository              ml-stack
Primary CLI             ml-stack
Primary Skill           /ml-stack
Python package          ml_stack
Remote daemon           ml-stackd
Environment prefix      ML_STACK_
User config             ~/.config/ml-stack/
User cache              ~/.cache/ml-stack/
User data               ~/.local/share/ml-stack/       # platform-adjusted
Project state           .ml-stack/
Project requirements    requirements.md
Experiments             exp/
Research notebook       research/
Benchmarks              bench/
Scientific notes        notes/
```

Legacy development names from earlier design drafts are not part of the public product contract. An implementation MAY provide temporary migration aliases, but generated files and documentation MUST use `ml-stack`.

The Skill namespace uses kebab case. The tool/MCP namespace uses a stable structured namespace such as `ml_stack.*` so host-specific command spelling does not leak into the core.

---

# 99. Canonical end-to-end autonomous algorithm

This section is normative. It defines what `/ml-stack` means when invoked on a project or challenge directory.

## 99.1 Startup

On invocation, ML-Stack SHALL:

1. identify the current project root;
2. load host/system permissions and available tools;
3. load user-level ML-Stack configuration;
4. load team/project configuration;
5. restore an unfinished ML-Stack session when safe, or create a new session;
6. discover `requirements.md` and all explicit user instructions;
7. discover challenge/project descriptions, README files, AGENTS files, rules, sample outputs, source code, notebooks, datasets, and build metadata;
8. hash the relevant project inputs;
9. create or update `.ml-stack/manifest.json`;
10. create the default human-readable lab directories if absent;
11. start the event stream, heartbeat, experiment ledger, and resource monitor.

## 99.2 Requirements capture and lock

Before broad experimentation, ML-Stack SHALL persist the user's requirements as human-readable Markdown. It MUST NOT assume that the desired output is `solution.py`, `submission.csv`, a leaderboard entry, or even source code.

The system keeps two linked representations:

```text
requirements.md                       human source of truth
.ml-stack/requirements/lock.yaml      compiled machine contract
```

The Markdown file preserves the user's wording. The compiled lock extracts:

```text
objective
metric and direction
target score or success threshold
input contract
output/deliverable contract
runtime interface
resource constraints
CPU/GPU requirements
network permissions
external-data permissions
pretrained-model permissions
prohibited methods
held-out/test isolation rules
validation requirements
reproducibility requirements
comment/style/file restrictions
runtime limits
memory limits
platform checks
required reports
required publication actions
approval boundaries
budget boundaries
```

Every experiment, promoted version, benchmark, and final deliverable MUST reference a requirements-lock revision hash.

## 99.3 Contract conflict handling

ML-Stack MUST detect contradictory requirements instead of silently choosing a convenient interpretation. Contradictions are represented in `.ml-stack/requirements/conflicts.json` and summarized in `notes/task.md`.

Resolution precedence is:

```text
1. Safety and host/platform policy
2. Official challenge/evaluation rules
3. Current explicit user instruction
4. Project/repository instructions
5. Team ML-Stack configuration
6. User-global ML-Stack configuration
7. ML-Stack defaults
```

When two rules at the same precedence conflict, the more specific rule wins only when the relationship is unambiguous. Otherwise ML-Stack SHALL use the safest non-destructive interpretation and mark the ambiguity. If the ambiguity makes valid execution impossible, request approval/clarification rather than fabricating compliance.

## 99.4 Discovery and task modeling

ML-Stack SHALL inspect the project without contaminating held-out evaluation data. It creates:

```text
notes/task.md
notes/data.md
.ml-stack/contracts/project.json
.ml-stack/contracts/data.json
.ml-stack/contracts/deliverables.json
```

The discovery model captures, where applicable:

```text
task family
modality/modalities
supervision type
train/validation/test roles
group structure
duplicate/near-duplicate structure
target schema
metric implementation
submission/output schema
runtime command
installed libraries
available pretrained assets
data volume
sequence/image/audio dimensions
class/target distributions
missingness
known leakage vectors
resource profile
estimated experiment costs
```

## 99.5 Validation lock

Before architecture search, ML-Stack SHALL create and lock a validation protocol appropriate to the hidden/evaluation setting. The lock includes:

```text
split strategy
random/group/time/entity keys
number of folds or holdout fraction
seed policy
preprocessing-fit boundary
metric implementation
aggregation rule
selection rule
confidence/stability reporting
protocol version
```

A protocol change starts a new comparison family. ML-Stack MUST NOT directly rank scores from incompatible validation protocols as though they are the same experiment series.

## 99.6 Research pass

ML-Stack SHALL decide whether literature/web/docs/code research is useful and, when permitted, perform it before expensive training. Research uses independent worker context so source exploration does not flood the main agent context.

Outputs are persisted under `research/` and converted into testable hypotheses rather than vague advice.

## 99.7 Baselines

ML-Stack SHALL establish multiple meaningful baselines when the task warrants them. Baselines must be legitimate under active requirements. A baseline is an experiment, not a permanent final method.

## 99.8 Hypothesis queue

The system maintains a queue with each item containing:

```text
hypothesis_id
claim
mechanism
source/evidence
expected effect
expected cost
risk
required compute
comparison parent
minimum evidence needed
status
```

The queue is prioritized by expected information gain and expected objective improvement per unit cost, while reserving some exploration budget for substantially different methods.

## 99.9 Experiment loop

For each experiment:

1. create `exp/<id>-<slug>/`;
2. write hypothesis and configuration before training;
3. resolve code/artifact parentage;
4. allocate compute;
5. launch with an immutable run spec;
6. stream logs and heartbeats;
7. detect technical failure vs scientific failure;
8. collect metrics, resource use, predictions where permitted, and artifacts;
9. run the evaluator/result judge;
10. write analysis and decision;
11. update the experiment ledger;
12. update notes and backlog;
13. extract reusable lessons only after evidence thresholds are met;
14. continue until the stopping policy triggers.

Technical retries do not count as scientific improvements. Silent changes to batch size, seed, data split, architecture, or preprocessing are forbidden; every such change creates a new run spec.

## 99.10 Promotion

An experiment can become promoted version `vN` only if it passes:

```text
requirements compliance
validation comparability
metric gate
artifact integrity
reproducibility gate
resource feasibility
held-out isolation audit
security audit
runtime interface audit
```

Promoted versions are immutable bundles. Final exported filenames are derived from the requirements contract, not from fixed ML-Stack assumptions.

## 99.11 Finalization

When model selection is complete, ML-Stack SHALL perform any required final retraining, frozen inference, packaging, schema checks, compilation/syntax checks, smoke tests, runtime tests, and deliverable verification.

## 99.12 Completion

A run is `DONE` only when:

```text
all required deliverables exist
all required deliverables pass their validators
best measured approach is identified
experiment ledger is consistent
research and decision notes are written
final report is written
orphan jobs/resources are reconciled
reusable lessons have been considered for promotion to memory
the system can state what was measured vs estimated vs unknown
```

If a requested target score was not reached, ML-Stack MUST say so explicitly. It may still finalize the strongest measured pipeline if the stopping budget is exhausted.

---

# 100. Canonical project filesystem contract

A default ML-Stack project SHOULD converge on this structure:

```text
project/
├── requirements.md
├── exp/
│   ├── 0001-baseline-a/
│   │   ├── hypothesis.md
│   │   ├── config.yaml
│   │   ├── run.json
│   │   ├── environment.json
│   │   ├── metrics.json
│   │   ├── resources.json
│   │   ├── analysis.md
│   │   ├── stdout.log
│   │   ├── stderr.log
│   │   └── artifacts/
│   └── ...
├── research/
│   ├── index.md
│   ├── papers.md
│   ├── web.md
│   ├── docs.md
│   ├── code.md
│   ├── datasets.md
│   ├── changelog.md
│   ├── evidence.jsonl
│   └── synthesis.md
├── bench/
│   ├── index.md
│   ├── models.md
│   ├── hardware.md
│   ├── providers.md
│   ├── runtime.jsonl
│   ├── memory.jsonl
│   ├── throughput.jsonl
│   └── regressions/
├── notes/
│   ├── task.md
│   ├── data.md
│   ├── validation.md
│   ├── decisions.md
│   ├── failures.md
│   ├── ideas.md
│   ├── progress.md
│   └── final.md
└── .ml-stack/
    ├── manifest.json
    ├── config.toml
    ├── state.json
    ├── sessions/
    ├── events/
    ├── requirements/
    ├── contracts/
    ├── ledger.sqlite
    ├── runs/
    ├── versions/
    ├── cache/
    ├── staged/
    ├── locks/
    ├── traces/
    ├── telemetry/
    └── parity/
```

The human-readable directories are intentionally separate from private/runtime state. A user should be able to understand the project by reading `requirements.md`, `research/`, `bench/`, `notes/`, and `exp/` without opening the internal database.

Large remote artifacts MAY remain remote when downloading them would be wasteful. Their local artifact record must contain content hashes, provider, URI/reference, access policy, provenance, and retention state.

---

# 101. `requirements.md` is universal, not competition-specific

ML-Stack supports leaderboard challenges, research projects, fine-tuning jobs, inference systems, benchmark suites, ablations, replication studies, dataset work, model conversion, deployment evaluations, and custom ML engineering tasks.

Therefore, `requirements.md` SHALL be expressive enough to describe arbitrary outputs.

## 101.1 Canonical template

```markdown
# ML-Stack Requirements

## User Directive
<verbatim or faithfully preserved current user request>

## Objective
<what success means>

## Mode
- challenge | research | training | evaluation | benchmarking | data | inference | deployment | other

## Inputs
- <files, directories, repos, datasets, arguments>

## Required Deliverables
- <exact required files/actions>

## Runtime Interface
<how outputs are executed or consumed>

## Metric / Success Criteria
- primary metric:
- direction:
- target:
- secondary metrics:

## Validation Requirements
<split/group/time/fold constraints>

## Experimentation Policy
<aggressiveness, ablations, seeds, ensembles, search budget>

## Held-out / Test Isolation
<exact restrictions>

## Development Compute
- CPU:
- GPU:
- RAM:
- VRAM:
- wall-time:

## Final Compute
- CPU:
- GPU:
- RAM:
- VRAM:
- wall-time:
- accelerator required:
- fallback required:

## Network Policy
- development research:
- training:
- final inference:
- external APIs:

## External Data / Pretrained Assets
<allowed/prohibited>

## Allowed Methods
<explicit permissions>

## Prohibited Methods
<explicit prohibitions>

## Reproducibility
<seeds, deterministic requirements, dependencies>

## File / Style Constraints
<comments, filenames, schemas, packaging, compilation, linting>

## Research Policy
<papers, docs, web, code search expectations>

## Benchmarking Policy
<quality/runtime/memory/provider/hardware expectations>

## Notes / Reporting
<what documentation must be left behind>

## Cross-project Learning
- allow reusable non-sensitive lessons: yes | no
- allow raw project examples globally: yes | no

## Budgets and Approvals
<time, money, experiment count, destructive operations>
```

## 101.2 Natural-language capture

If the user never writes this file manually, ML-Stack generates it from the conversation and project rules. The generated file MUST distinguish:

```text
USER-EXPLICIT
PROJECT-DISCOVERED
PLATFORM-DISCOVERED
ML-STACK-DEFAULT
```

so defaults are never mistaken for user requirements.

## 101.3 Examples of profile variance

ML-Stack must correctly support mutually different projects such as:

```text
GPU-only final training with no CPU fallback
CPU-only final execution with no CUDA usage
source-code-only deliverable
checkpoint + metrics + report deliverables
notebook deliverable
library/package deliverable
Docker image deliverable
Hub repository publication
benchmark report only
research-only replication with no submission file
```

No output name is globally special.

---

# 102. Experiment workspace and experiment record specification

## 102.1 Directory naming

Default experiment directories are:

```text
exp/0001-baseline-linear/
exp/0002-char-model/
exp/0003-gru-contrastive/
...
```

IDs are monotonically increasing within a project. Slugs are descriptive but never used as identity.

## 102.2 Required files

Each scientific experiment SHALL have:

```text
hypothesis.md       pre-run scientific claim and expected outcome
config.yaml         normalized hyperparameters and data/validation refs
run.json            immutable execution identity/provenance
environment.json    software/hardware/provider snapshot
metrics.json        machine-readable measurements
resources.json      runtime/RAM/VRAM/throughput/cost measurements
analysis.md         post-run interpretation and decision
```

Optional files:

```text
predictions.*
confusion_matrix.*
curves.*
profiles.*
stdout.log
stderr.log
artifacts/
checkpoints/
```

## 102.3 `run.json`

It includes at least:

```json
{
  "run_id": "run_...",
  "experiment_id": "exp_...",
  "parent_run_id": null,
  "requirements_revision": "sha256:...",
  "validation_protocol": "val_v1",
  "code_hash": "sha256:...",
  "data_hashes": {},
  "seed": 42,
  "provider": "local",
  "hardware": {},
  "command": [],
  "started_at": "...",
  "ended_at": "...",
  "status": "completed"
}
```

## 102.4 Scientific status

An experiment has separate technical and scientific states:

```text
technical: queued | provisioning | running | completed | failed | cancelled | lost
scientific: unjudged | promote | reject | inconclusive | robustness_required | invalid_comparison
```

A crashed run must never be reported as a negative scientific result unless enough of the intended experiment completed to support that inference.

## 102.5 Experiment lineage

Every experiment can point to:

```text
parent experiment
source paper/evidence IDs
knowledge-card IDs
dataset-contract version
validation-protocol version
requirements version
promoted version, if any
```

This makes the project a provenance graph rather than a folder of anonymous scripts.

---

# 103. Research notebook, source intelligence, and learning-from-papers system

Research is not a one-off search box. It is a durable subsystem.

## 103.1 Source families

The research engine SHALL support, when host/network permissions allow:

```text
web search
browser/open-page/follow-link workflows
arXiv
Semantic Scholar-style metadata/citations
Hugging Face Papers
paper PDF/full text
paper section extraction
citation graph traversal
related/recommended papers
model discovery
dataset discovery
collection/resource discovery
official documentation
documentation navigation
OpenAPI specification discovery
dynamic API tool generation
GitHub repository search
GitHub code/example search
GitHub file reading
release/changelog search
model cards
dataset cards
benchmark pages
issue/PR discussions when useful
local repository/docs search
```

## 103.2 Paper workflow

A paper research worker SHOULD:

1. identify 2-5 anchor papers;
2. read abstract/intro only for triage;
3. read methods, experiments, ablations, and limitations for shortlisted work;
4. follow important citations and downstream work;
5. capture exact datasets, metric definitions, model sizes, preprocessing, hyperparameters, and reported numbers;
6. find maintained code when available;
7. assess implementation feasibility under the active requirements;
8. turn findings into ranked experiment recipes;
9. cite the evidence in `research/papers.md` and `research/evidence.jsonl`.

## 103.3 Evidence records

Each durable claim should include:

```text
evidence_id
source_type
source_title
source_locator
retrieved_at
claim
scope
quoted_or_paraphrased
confidence
paper_section/page when known
relevance to current task
implementation implications
staleness policy
```

## 103.4 Web/docs/code notes

`research/web.md`, `docs.md`, and `code.md` SHALL record not only links but what was learned, why it matters, and which hypothesis it supports.

## 103.5 Source trust and freshness

ML-Stack favors:

```text
official docs/source > primary paper/repository > authoritative benchmark > strong secondary source > community discussion
```

Freshness matters for APIs, libraries, provider quotas, hardware availability, model releases, and hosted services. Stable theoretical claims can use older sources.

## 103.6 Research caching

Research results are content-addressed and cached. Repeated agents should not rediscover the same paper from scratch unless staleness or a new task-specific question warrants it.

## 103.7 Research-to-experiment conversion

Research never promotes a method directly. It produces hypotheses such as:

```text
"Paper X's pairwise ranking loss may improve this candidate-order metric because ..."
```

That hypothesis must still be validated on the current project.

---

# 104. Benchmarking and empirical systems knowledge

ML-Stack maintains benchmarking as a separate discipline from model selection.

## 104.1 Benchmark dimensions

Depending on task, benchmarks may record:

```text
validation quality
training time
inference latency
examples/sec
tokens/sec
images/sec
GPU utilization
VRAM peak
RAM peak
CPU utilization
I/O throughput
startup/provisioning latency
provider queue time
failure rate
cost
energy estimate when available
artifact size
cold-start time
compile time
```

## 104.2 Model benchmark registry

Model records include task signature, data size, representation, parameter count, precision, compiler/backend, batch size, sequence/resolution, quality metric, runtime, memory, and environment.

## 104.3 Hardware registry

ML-Stack learns empirical scaling across hardware without assuming theoretical peak FLOPS predicts end-to-end speed. Hardware cards can record:

```text
GPU/CPU model
VRAM/RAM
framework versions
supported dtypes
measured throughput by workload shape
OOM boundaries
known instability
cost/provider context
```

## 104.4 Provider registry

Provider cards track:

```text
available hardware
queue/start latency
job reliability
preemption behavior
storage behavior
network policy
secret injection
artifact retrieval
cost/credit behavior
scheduled jobs support
known limits
```

## 104.5 Regression benchmarks

ML-Stack itself SHALL have regression fixtures so changes to runtime, providers, parsers, validation, and result judging can be measured rather than assumed safe.

---

# 105. Continuous learning across projects

The user's requirement that ML-Stack should get more useful as it trains more models is a core product feature, not an optional analytics layer.

## 105.1 Memory scopes

ML-Stack maintains three separable scopes:

```text
project memory      this repository/challenge only
workspace memory    a team or user-selected collection of projects
user-global memory  reusable ML lessons across projects
```

The default global store contains distilled non-sensitive knowledge, not raw project data.

## 105.2 What can be learned

Eligible reusable knowledge includes:

```text
model-family performance by task signature
representation effectiveness
hyperparameter priors
optimizer/scheduler priors
augmentation priors
validation design lessons
ensemble complementarity patterns
failure/OOM signatures
VRAM and RAM estimates
hardware throughput observations
provider reliability observations
paper-to-implementation mappings
library/API gotchas
runtime-safe defaults
data-size scaling behavior
seed instability patterns
calibration behavior
common leakage risks
successful debugging strategies
negative results with enough evidence
```

## 105.3 Knowledge card

A promoted reusable lesson is stored as a structured card:

```yaml
id: kc_...
title: char-cnn-helps-short-noisy-text
claim: ...
task_signature:
  modality: text
  objective: classification
  data_scale: small
conditions:
  - ...
evidence:
  projects: 4
  runs: 11
  effect_mean: ...
  effect_range: ...
  protocols: [...]
confidence: medium
counterevidence: [...]
created_at: ...
last_verified_at: ...
expires_or_review_after: ...
privacy: distilled
```

## 105.4 Promotion thresholds

One run is not enough for a universal rule. Knowledge promotion considers:

```text
number of independent runs
number of projects
effect size
stability
protocol comparability
recency
contradictory evidence
task similarity
```

A project-specific insight can be high confidence locally while remaining low confidence globally.

## 105.5 Negative knowledge

The system learns from failed ideas too. Example:

```text
"Large transformer from scratch consistently overfits <5k examples on this task family under 30-minute budgets."
```

Negative knowledge reduces repeated waste but never permanently bans retesting when task conditions differ.

## 105.6 Retrieval

At project start and before hypothesis ranking, ML-Stack builds a task signature and retrieves relevant cards. Retrieval uses structured filters first and semantic similarity second when available.

Retrieved memory is evidence, not truth. It must be cited in the hypothesis record and may be overridden by current measured results.

## 105.7 Staleness and contradiction

Knowledge cards can decay. New contradictory results decrease confidence. API/provider facts have shorter TTL than model-behavior observations. ML-Stack records supersession rather than deleting history.

## 105.8 Privacy and anti-leakage

Global memory MUST NOT contain by default:

```text
held-out answers
test predictions
row-level labels from private projects
secrets/tokens
proprietary raw data
personally identifying data
challenge-specific prohibited metadata
exact hidden-evaluation content
```

Cross-project learning is disabled or narrowed when requirements prohibit it.

## 105.9 Meta-learning loop

After a project or a sufficiently large experiment batch:

```text
runs -> summarize evidence -> detect reusable patterns -> propose cards ->
privacy/leakage check -> confidence scoring -> promote/reject -> index
```

Over time this should improve experiment ordering, resource estimation, and model priors without turning the system into an opaque hardcoded-answer database.

---

# 106. Full Skill and plugin capability inventory

Every durable ML-Stack capability SHALL be available through the canonical runtime and SHOULD have a corresponding Skill entrypoint when direct invocation is useful.

```text
/ml-stack                    full autonomous project/challenge loop
/ml-stack-requirements       capture, compile, diff, lock requirements
/ml-stack-inspect            project/task/data inspection
/ml-stack-plan               plan/todo/state-machine control
/ml-stack-research           coordinated literature/web/docs/code research
/ml-stack-papers             papers, citations, full text, related resources
/ml-stack-web                web/browser research
/ml-stack-docs               docs navigation/fetch/OpenAPI discovery
/ml-stack-github             code/example/repository research
/ml-stack-dataset            dataset inspection/schema/sampling validation
/ml-stack-experiment         create/run/retry/compare experiments
/ml-stack-evaluate           metrics, validation, error analysis
/ml-stack-benchmark          model/hardware/provider/regression benchmarking
/ml-stack-ensemble           ensemble search and validation
/ml-stack-compute            resource planning and provider selection
/ml-stack-jobs               submit/list/log/inspect/cancel/schedule jobs
/ml-stack-sandbox            create/replace/inspect/destroy remote sandboxes
/ml-stack-artifacts          artifact registry/staging/download/upload
/ml-stack-repo               branches/tags/PRs/repository operations
/ml-stack-notify             gateway notifications
/ml-stack-notes              maintain scientific notebook
/ml-stack-learn              retrieve/extract/promote reusable knowledge
/ml-stack-status             project/session/job/experiment status
/ml-stack-usage              usage, budgets, cost, quota, KPI views
/ml-stack-sessions           list/resume/export/clear session state
/ml-stack-autonomy           approvals/auto-approval/budget policy
/ml-stack-backlog            prioritize hypotheses/technical debt/research
/ml-stack-cleanup            orphan/stale resource cleanup
/ml-stack-publish            publish artifacts/repos/reports
/ml-stack-traces             trace visibility/export/share controls
/ml-stack-sft                build/filter/tag trajectory datasets
/ml-stack-kpi                build/schedule KPI aggregation
/ml-stack-model              model selection/switching/capability probing
```

The Skills do not fork logic. They call the same underlying MCP/runtime APIs.

---

# 107. Tool/MCP contract — expanded complete surface

The following is the target stable tool namespace. Exact transport schemas may evolve under semantic versioning, but capabilities are normative.

## 107.1 Project and requirements

```text
ml_stack.project.discover
ml_stack.project.manifest
ml_stack.project.status
ml_stack.requirements.capture
ml_stack.requirements.compile
ml_stack.requirements.diff
ml_stack.requirements.lock
ml_stack.requirements.audit
ml_stack.requirements.list_conflicts
```

## 107.2 Files and execution

```text
ml_stack.fs.read
ml_stack.fs.write
ml_stack.fs.edit
ml_stack.fs.list
ml_stack.exec.run
ml_stack.exec.stream
ml_stack.exec.cancel
```

Local and sandbox runtimes must implement the same logical contract.

## 107.3 Data

```text
ml_stack.data.inspect
ml_stack.data.schema
ml_stack.data.sample
ml_stack.data.splits
ml_stack.data.hash
ml_stack.data.duplicates
ml_stack.data.near_duplicates
ml_stack.data.groups
ml_stack.data.validate_training_schema
ml_stack.data.stage
ml_stack.data.unstage
```

## 107.4 Validation/evaluation

```text
ml_stack.validation.create
ml_stack.validation.lock
ml_stack.validation.compare
ml_stack.validation.audit_fit_boundaries
ml_stack.metric.resolve
ml_stack.metric.run
ml_stack.errors.analyze
```

## 107.5 Research

```text
ml_stack.research.run
ml_stack.research.status
ml_stack.papers.trending
ml_stack.papers.search
ml_stack.papers.details
ml_stack.papers.read
ml_stack.papers.citations
ml_stack.papers.snippets
ml_stack.papers.recommend
ml_stack.papers.find_datasets
ml_stack.papers.find_models
ml_stack.papers.find_collections
ml_stack.papers.find_resources
ml_stack.web.search
ml_stack.web.open
ml_stack.web.follow
ml_stack.docs.explore
ml_stack.docs.fetch
ml_stack.openapi.discover
ml_stack.openapi.invoke
ml_stack.github.find_examples
ml_stack.github.list_repos
ml_stack.github.read_file
```

## 107.6 Planning/backlog

```text
ml_stack.plan.get
ml_stack.plan.update
ml_stack.plan.normalize
ml_stack.hypothesis.create
ml_stack.hypothesis.rank
ml_stack.backlog.list
ml_stack.backlog.prioritize
```

## 107.7 Experiments and versions

```text
ml_stack.experiment.create
ml_stack.experiment.launch
ml_stack.experiment.retry
ml_stack.experiment.cancel
ml_stack.experiment.compare
ml_stack.experiment.judge
ml_stack.experiment.list
ml_stack.version.promote
ml_stack.version.list
ml_stack.version.materialize
```

## 107.8 Compute/jobs

```text
ml_stack.compute.capabilities
ml_stack.compute.estimate
ml_stack.compute.select_provider
ml_stack.job.run
ml_stack.job.list
ml_stack.job.logs
ml_stack.job.inspect
ml_stack.job.cancel
ml_stack.job.schedule_create
ml_stack.job.schedule_list
ml_stack.job.schedule_inspect
ml_stack.job.schedule_delete
ml_stack.job.schedule_suspend
ml_stack.job.schedule_resume
```

## 107.9 Sandbox

```text
ml_stack.sandbox.create
ml_stack.sandbox.replace
ml_stack.sandbox.status
ml_stack.sandbox.exec
ml_stack.sandbox.read
ml_stack.sandbox.write
ml_stack.sandbox.edit
ml_stack.sandbox.destroy
ml_stack.sandbox.list
```

## 107.10 Artifacts/repositories

```text
ml_stack.artifact.register
ml_stack.artifact.list
ml_stack.artifact.fetch
ml_stack.artifact.publish
ml_stack.repo.files.list
ml_stack.repo.files.read
ml_stack.repo.files.write
ml_stack.repo.branch.create
ml_stack.repo.branch.delete
ml_stack.repo.refs.list
ml_stack.repo.tag.create
ml_stack.repo.tag.delete
ml_stack.repo.pr.create
ml_stack.repo.pr.list
ml_stack.repo.pr.get
ml_stack.repo.pr.merge
ml_stack.repo.pr.close
ml_stack.repo.pr.comment
ml_stack.repo.pr.change_status
ml_stack.repo.create
ml_stack.repo.update
```

## 107.11 Notifications

```text
ml_stack.notify.send
ml_stack.notify.destinations
ml_stack.notify.test
```

## 107.12 Sessions/traces

```text
ml_stack.session.list
ml_stack.session.get
ml_stack.session.resume
ml_stack.session.interrupt
ml_stack.session.clear
ml_stack.session.export
ml_stack.trace.status
ml_stack.trace.export
ml_stack.trace.set_visibility
```

## 107.13 Usage/telemetry/KPIs

```text
ml_stack.usage.current
ml_stack.usage.estimate
ml_stack.usage.thresholds
ml_stack.usage.history
ml_stack.kpi.build
ml_stack.kpi.schedule
ml_stack.telemetry.status
```

## 107.14 Benchmark/memory

```text
ml_stack.benchmark.run
ml_stack.benchmark.compare
ml_stack.benchmark.models
ml_stack.benchmark.hardware
ml_stack.benchmark.providers
ml_stack.memory.retrieve
ml_stack.memory.propose
ml_stack.memory.promote
ml_stack.memory.reject
ml_stack.memory.audit
```

## 107.15 Maintenance

```text
ml_stack.cleanup.scan
ml_stack.cleanup.apply
ml_stack.parity.scan
ml_stack.parity.report
ml_stack.doctor
```

---

# 108. ML Intern snapshot parity — exhaustive functional mapping

ML-Stack deliberately re-expresses the full functional surface of the pinned Hugging Face ML Intern snapshot as portable plugin/Skill/runtime capabilities. It does **not** require cloning ML Intern's visual frontend or terminal aesthetics. Presentation can be host-native; function cannot be silently dropped.

Pinned upstream snapshot:

```text
repository: huggingface/ml-intern
commit: b0d6752723d17ef2ea7a54f5aeb63abebba99e47
```

The parity scanner described earlier remains the authoritative guard against future upstream additions.

## 108.1 Agent configuration

Upstream functional themes from `agent/config.py` map to:

```text
config loading and overrides
local vs sandbox tool runtime
model selection
reasoning-effort preference
trace-sharing configuration
personal trace destination
messaging configuration
auto file upload settings
host/user config precedence
```

ML-Stack implements these through config schemas plus host adapters.

## 108.2 Context manager

`agent/context_manager/manager.py` implies equivalents for:

```text
message history
context-size accounting
auto compaction
compaction summaries
recovery from oversized context
preservation of tool-call continuity
session-upload hooks
```

ML-Stack adds project-note offloading so scientific state is not trapped in model context.

## 108.3 Agent loop

`agent/core/agent_loop.py` maps to:

```text
submission/operation queue
streaming and non-streaming model calls
tool-call parsing
parallel/sequential tool execution policy
approval interception
tool state events
iteration limits
interrupts
continuation behavior
malformed tool-call recovery
dangling tool-call repair
no-tool continuation guard
LLM error classification
thinking/reasoning history handling
doom-loop checks
context compaction integration
```

## 108.4 Approval policy

`approval_policy.py` maps to policy-based approval classes for:

```text
compute spend
remote job creation
sandbox creation/replacement
destructive file/repo actions
publication
secret-bearing operations
high-cost model calls
```

Auto-approval can be enabled only inside explicit bounded budgets.

## 108.5 Cost estimation

`cost_estimation.py` maps to preflight and post-run estimates for:

```text
LLM inference
remote compute
storage where measurable
provider jobs
research calls
```

Actual and estimated cost are stored separately.

## 108.6 Doom-loop protection

`doom_loop.py` maps to detection of:

```text
identical repeated tools
near-identical repeated arguments
polling without state change
error/retry spirals
compaction spirals
research-query loops
experiment retry loops
```

Corrective behavior can include a prompt, backoff, alternate tool, or hard stop.

## 108.7 Reasoning-effort probing

`effort_probe.py` maps to:

```text
user effort preference
provider/model capability probe
fallback cascade
per-model cache of accepted effort
safe stripping of unsupported reasoning parameters
```

Host models that manage effort natively can mark this as host-provided-equivalent.

## 108.8 Hugging Face access and tokens

`hf_access.py` and `hf_tokens.py` map to:

```text
token discovery
access validation
scope-aware tool enablement
token propagation to HF-backed actions
clear auth diagnostics
secret redaction
```

These remain provider-specific plugins inside a provider-neutral system.

## 108.9 Model/provider catalogs

`hf_router_catalog.py`, `model_ids.py`, `model_switcher.py`, and `llm_params.py` map to:

```text
model catalog discovery
canonical model IDs
runtime model switching where host allows
parameter normalization
provider-specific capability handling
suggested model listing
local/hosted distinction
```

## 108.10 Local models

`local_models.py` maps to OpenAI-compatible local endpoints including the ML Intern-supported families:

```text
Ollama
vLLM
LM Studio
llama.cpp
```

ML-Stack MAY add other endpoints, but must preserve these compatibility patterns.

## 108.11 Prompt caching

`prompt_caching.py` maps to provider-aware prompt-prefix caching and stable system/tool prefix construction where supported. Caching behavior must never alter scientific results through stale project state.

## 108.12 Redaction

`redact.py` maps to redaction of secrets/tokens from:

```text
logs
traces
notifications
telemetry
research artifacts
error reports
```

## 108.13 Sessions

`session.py`, `session_persistence.py`, and `session_resume.py` map to:

```text
session identity
context and state persistence
model/effort state
sandbox/job references
resume after restart
interrupted-turn handling
new/clear semantics
session history
```

## 108.14 Session uploader and trace sharing

`session_uploader.py` maps to:

```text
trajectory serialization
private-by-default personal trace storage
continuous/idempotent upload
visibility status
public/private changes
custom destination
opt-out
```

ML-Stack supports HF trace repositories when configured and generic/local trace stores otherwise.

## 108.15 Telemetry, usage metrics, and thresholds

`telemetry.py`, `usage_metrics.py`, and `usage_thresholds.py` map to:

```text
per-turn/model/tool usage
session usage
cost/usage counters
threshold warnings
threshold approval gates
optional anonymized telemetry
local metrics even when remote telemetry is disabled
```

## 108.16 YOLO/autonomy budget

`yolo_budget.py` maps to bounded autonomy with:

```text
auto-approval state
budget ceilings
usage-aware gating
safe shutdown at limits
sandbox/compute budget integration
```

ML-Stack uses the clearer public term `autonomy`, while allowing a `yolo` compatibility alias if desired.

## 108.17 Core tool registration/router

`agent/core/tools.py` maps every registered upstream tool family into the ML-Stack tool registry, with provider-neutral interfaces where possible.

## 108.18 Messaging

`agent/messaging/base.py`, `gateway.py`, `models.py`, and `slack.py` map to:

```text
notification gateway abstraction
destination models
outbound event routing
Slack Web API implementation
auto events for approval/error/completion
agent-triggered notifications
provider capability and permission checks
```

## 108.19 Prompts

The versioned upstream system prompts map conceptually to versioned Skill/runtime instruction bundles. ML-Stack keeps prompt/Skill behavior under source control with migration tests, rather than hiding critical scientific rules in ad-hoc runtime strings.

## 108.20 SFT tagger

`agent/sft/tagger.py` maps to trajectory tagging by:

```text
tool usage
outcome
HF/provider job status
GPU family
multi-GPU
sandbox usage
feedback
model family
turn bucket
cost bucket
task type
```

ML-Stack extends tags with requirements revision, validation protocol, experiment ID, provider, task signature, and promoted version.

## 108.21 Dataset tools

`dataset_tools.py` maps to inspection of:

```text
dataset status
configs
splits
schema/features
sample rows
parquet metadata
training-schema expectations
SFT schema
DPO schema
GRPO schema
```

ML-Stack generalizes beyond HF datasets to local files, object stores, SQL/Arrow/Parquet, images, audio, and project-defined loaders.

## 108.22 Documentation tools

`docs_tools.py` maps to documentation exploration and fetching across the HF ecosystem plus generic docs/OpenAPI sources. The upstream breadth of supported HF docs remains available through an HF docs provider.

## 108.23 Edit utilities

`edit_utils.py` maps to safe patch/edit primitives with:

```text
exact-match edits
conflict/error reporting
atomic writes where possible
path-boundary checks
diff capture
```

## 108.24 GitHub example/repository/file research

`github_find_examples.py`, `github_list_repos.py`, and `github_read_file.py` map to read-oriented code research with result ranking, repository metadata, and targeted file retrieval.

## 108.25 HF repository files

`hf_repo_files_tool.py` maps to listing, reading, and writing Hub repository files with artifact provenance and authentication checks.

## 108.26 HF repository git operations

`hf_repo_git_tool.py` maps all observed operation families:

```text
create_branch
delete_branch
list_refs
create_tag
delete_tag
create_pr
list_prs
get_pr
merge_pr
close_pr
comment_pr
change_pr_status
create_repo
update_repo
```

## 108.27 HF Jobs

`jobs_tool.py` maps all observed immediate and scheduled operations:

```text
run
ps/list
logs
inspect
cancel
scheduled run/create
scheduled ps/list
scheduled inspect
scheduled delete
scheduled suspend
scheduled resume
```

It preserves environment variables, secret injection, hardware flavor selection, namespace handling, long-running log behavior, and Trackio integration when applicable.

## 108.28 Local tools

`local_tools.py` maps local:

```text
bash
read
write
edit
```

with project boundary/security controls.

## 108.29 Notification tool

`notify_tool.py` maps agent-initiated outbound messages through the configured notification gateways.

## 108.30 Papers tool

`papers_tool.py` maps the full observed operation set:

```text
trending
search
paper_details
read_paper
citation_graph
snippet_search
recommend
find_datasets
find_models
find_collections
find_all_resources
```

Filters and section-specific reading are preserved where source APIs support them.

## 108.31 Plan tool

`plan_tool.py` maps structured todos/plans, normalization, state updates, and user-visible progress.

## 108.32 Research subagent

`research_tool.py` maps to an independent-context, read-oriented research worker with paper-first behavior, literature crawling, dataset/code validation, iteration/context limits, and doom-loop protection.

## 108.33 Sandbox client and tool

`sandbox_client.py` and `sandbox_tool.py` map to:

```text
private remote sandbox creation
auto-start where configured
explicit GPU/non-default hardware creation
sandbox replacement
remote bash/read/write/edit
status/auth handling
session-linked lifetime
safe cleanup
```

## 108.34 Trackio seeding

`trackio_seed.py` maps to experiment tracking bootstrap/seed behavior and stable project/space identification.

## 108.35 Web search

`web_search_tool.py` maps to freshness-aware web research with source capture, errors/retries, and research-note integration.

## 108.36 Backend dataset uploads

`backend/dataset_uploads.py` maps to staged upload of local files/datasets for remote execution, including validation, content hashing, ownership, cleanup, and project/session linkage.

## 108.37 Backend dependencies and service startup

`backend/dependencies.py` and `backend/main.py` map to dependency injection/service wiring, startup health, auth-aware provider construction, and clean shutdown for the optional `ml-stackd` service.

## 108.38 KPI scheduler

`backend/kpis_scheduler.py` maps to scheduled aggregation of private/local or opt-in telemetry and experiment KPIs.

## 108.39 Backend models

`backend/models.py` maps to stable request/event/session DTOs used across remote clients. ML-Stack keeps API schemas versioned and backwards-compatible within a major version.

## 108.40 Backend agent routes

`backend/routes/agent.py` maps to remote session lifecycle, turn submission, event streaming, interrupt/control operations, file/data staging hooks, and status surfaces in `ml-stackd`.

## 108.41 Backend auth routes

`backend/routes/auth.py` maps to remote authentication/OAuth/session identity where remote mode is deployed. Local-only installations do not require a separate auth server.

## 108.42 Backend session manager

`backend/session_manager.py` maps to multi-session lifecycle, event fanout, heartbeats, persistence, expiry, reaping, recovery, and resource linkage.

## 108.43 Backend usage

`backend/usage.py` maps to usage aggregation, quota/threshold state, cost display, and usage APIs.

## 108.44 KPI build script

`scripts/build_kpis.py` becomes `ml-stack kpi build` / `/ml-stack-kpi`, producing experiment/runtime/usage summaries from traces and ledgers.

## 108.45 SFT build script

`scripts/build_sft.py` becomes `ml-stack sft build`, exporting filtered/tagged trajectories for legitimate internal training/evaluation uses.

## 108.46 Backlog prioritization script

`scripts/prioritize_backlog.py` maps both software backlog and scientific backlog prioritization, using model reasoning with bounded cost and explicit scoring criteria.

## 108.47 Orphan sandbox sweep

`scripts/sweep_orphan_sandboxes.py` maps to provider-neutral orphan detection and cleanup with dry-run, ownership checks, age thresholds, and audit logging.

## 108.48 Frontend feature parity without frontend duplication

The upstream frontend exposes functional concepts that ML-Stack SHALL surface through host-native UI/commands:

```text
activity/status indicator
assistant/user/tool-call rendering
error banners
expired-session state
Markdown rendering
code/artifact panel
job/upgrade/resource warnings
session sidebar/history
usage meter
welcome/onboarding state
autonomy control
research progress state
auth state
event-stream transport
```

ML-Stack does not require a React clone; Claude Code, Codex, ChatGPT, OpenCode, terminal, or another host can render the same state differently.

## 108.49 Reliability behavior implied by upstream tests

Parity releases SHALL include behavior equivalent to the upstream test intent for:

```text
model gating
HF/auth token propagation
auto-approval policy
KPI/SFT builders
local model CLI behavior
new/clear session semantics
context compaction loop breaking
cost estimation
dangling tool-call repair
dataset upload behavior
doom-loop and polling-loop detection
effort probing
heartbeats
Hub artifact handling
KPI scheduling
LLM error classification
LLM parameter normalization
malformed tool-argument recovery
messaging
no-tool continuation guard
personal trace repositories
plan normalization
prompt caching
secret redaction
sandbox active-state messaging
sandbox API auth
sandbox auto-start
private sandbox behavior
sandbox script resolution
sandbox autonomy budget
session-manager persistence
session persistence
session reaping
session resume
session upload
SFT tagging
telemetry/usage
thinking-history handling
Trackio identifiers
usage thresholds/approval
web search
autonomy/yolo budgets
```

These tests are treated as behavioral documentation, not merely CI implementation details.

---

# 109. Host-native packaging and install-once/use-everywhere contract

ML-Stack follows the gstack-style idea of one repository containing a capability pack that installs into multiple agent ecosystems.

## 109.1 Single source tree

Canonical content lives once:

```text
skills-src/
tools/
core/
providers/
adapters/
schemas/
templates/
```

Host-specific folders are generated/installed from that source rather than independently maintained copies.

## 109.2 Installer

Canonical flow:

```bash
git clone <ml-stack-repository> ~/ml-stack
cd ~/ml-stack
./setup
```

Supported options SHOULD include:

```text
--host claude-code
--host codex
--host chatgpt
--host opencode
--host all
--global
--project <path>
--dry-run
--update
--uninstall
--doctor
```

## 109.3 Host auto-detection

`./setup` detects installed/supported host directories and explains exactly what it will install before modifying global state.

## 109.4 Claude Code

Package as native Skills/plugin components with optional MCP server, hooks, agents, and commands where beneficial.

## 109.5 Codex

Install Agent Skills/instructions plus MCP configuration and any supported plugin metadata.

## 109.6 ChatGPT

Expose ML-Stack as a plugin/app/Skill bundle where available, backed by remote MCP when local filesystem/process access cannot be reached directly. `ml-stackd` is the bridge for secure remote access when required.

## 109.7 OpenCode

Use Agent Skills, plugin/custom-tool/MCP mechanisms, including compatible skill layouts where supported.

## 109.8 Generic hosts

Fallback contract:

```text
portable SKILL.md/instructions
MCP endpoint
CLI `ml-stack`
```

A host that can read instructions and call MCP can use the core system even without a bespoke adapter.

---

# 110. Model intelligence and agent orchestration policy

ML-Stack should be "smart and humble" across hosts whose reasoning models differ.

## 110.1 Host model first

By default, the host's current model is the orchestrator. ML-Stack does not force a separate proprietary model.

## 110.2 Optional worker models

Research or summarization workers MAY use a configured model/router/local endpoint when allowed. Their outputs are evidence records, not unquestioned instructions.

## 110.3 Specialist roles

Canonical roles include:

```text
Challenge/Project Analyst
Requirements Compiler
Research Lead
Paper Researcher
Documentation Researcher
Code Researcher
Data Scientist
Validation Designer
Experiment Designer
Experiment Runner
Resource Planner
Benchmark Engineer
Error Analyst
Skeptic/Reviewer
Result Judge
Compliance Auditor
Security Auditor
Release Auditor
Memory Curator
```

Roles are logical prompt/Skill contexts, not necessarily separate processes.

## 110.4 Independent context

Long research, log analysis, and codebase inspection SHOULD happen in bounded subcontexts. Findings return as structured summaries/evidence so the main context remains focused.

## 110.5 Epistemic labels

Every decision-support result uses:

```text
MEASURED
EXTERNALLY_OBSERVED
LITERATURE_EVIDENCE
ESTIMATED
HYPOTHESIS
UNKNOWN
```

No UI or report may blur these categories.

---

# 111. Compute plane — local and remote

ML-Stack's scientific workflow is provider-neutral.

## 111.1 Provider interface

Each provider implements capability discovery plus:

```text
submit
status
logs
cancel
artifacts
heartbeat/reconcile
secret injection
environment declaration
resource declaration
optional schedules
```

## 111.2 Initial providers

The target adapter set is:

```text
local process
Hugging Face Jobs
Hugging Face sandbox/private Space
Kaggle jobs/notebooks when programmatic use is permitted
Modal
SSH remote machine
Slurm cluster
```

Additional providers can be plugins.

## 111.3 Resource inference

Before expensive runs ML-Stack estimates:

```text
CPU vs GPU suitability
VRAM/RAM
expected wall time
disk
network needs
precision support
multi-GPU usefulness
```

## 111.4 Free-first does not mean imaginary-free

If configured `free_first = true`, ML-Stack queries actual available quota/capability and uses free/owned capacity when suitable. It MUST NOT assume a provider has a free tier or available accelerator without current evidence.

## 111.5 OOM adaptation

An OOM is a technical event. The runner may propose a new experiment configuration using smaller batch size, accumulation, checkpointing, truncation/resolution changes, precision changes, or a larger device. It must not silently mutate the current run.

## 111.6 Preemption/provider outage

Retries preserve the run spec unless an explicit new run is created. Provider outages are separated from scientific failures in the ledger.

---

# 112. Security, isolation, and trust boundaries

## 112.1 Retrieved content is untrusted

Papers, web pages, repositories, READMEs, model cards, notebooks, and datasets can contain instructions. Retrieved instructions never override the active requirements/policy hierarchy merely because they appear in text.

## 112.2 External code is untrusted

Research workers can inspect code read-only. Execution of external code requires the execution policy, preferably a sandbox for unknown repositories.

## 112.3 Secrets

Secrets are supplied through provider-native secret stores/environment injection, never copied into research notes, experiment Markdown, traces, or submissions.

## 112.4 Held-out/test isolation

The compliance engine tracks which data partitions can influence:

```text
fit
transform fitting
model selection
threshold selection
ensemble weighting
calibration
representation learning
statistics
clustering
pseudo-labeling
adaptation
```

Rules are requirements-specific. Some tasks legitimately require joint test-set assignment; others forbid any cross-test interaction. ML-Stack does not impose a universal assumption over explicit task rules.

## 112.5 File boundaries

Local tools default to project-root access plus configured ML-Stack state/cache directories. Broader filesystem access requires policy/approval.

---

# 113. Versioned deliverables without hardcoded filenames

ML-Stack distinguishes internal promoted versions from user-facing deliverables.

## 113.1 Internal bundle

```text
.ml-stack/versions/v1/
.ml-stack/versions/v2/
...
```

Each bundle includes:

```text
manifest.json
requirements-lock.yaml
source snapshot or source references
training config
validation evidence
metrics
resource estimates/measurements
artifact references
audit results
```

## 113.2 Export adapter

The deliverable contract may map a promoted version to any set, for example:

```text
solution_v1.py + submission.csv
train.py + infer.py + checkpoint.safetensors
model.onnx
notebook.ipynb
report.md
wheel package
Dockerfile + image tag
HF repository
JSON predictions
parquet dataset
benchmark report
```

## 113.3 Validation adapters

Deliverables can register validators such as:

```text
Python syntax/pycompile
unit tests
CLI smoke test
schema comparison
row/ID/order checks
JSON schema
checkpoint load test
ONNX runtime load
package build/import
container build
runtime budget smoke test
comment/style constraints
forbidden-import/network audit
```

---

# 114. Notes system — durable scientific context for future agents

The notes layer is deliberately plain Markdown so a different host/model can continue the project without special database access.

## 114.1 Required notes

`notes/task.md` — task definition and active requirements summary.  
`notes/data.md` — data structure, distributions, leakage observations.  
`notes/validation.md` — validation design and revisions.  
`notes/decisions.md` — major choices and evidence.  
`notes/failures.md` — technical and scientific failures.  
`notes/ideas.md` — unresolved hypotheses.  
`notes/progress.md` — concise running state.  
`notes/final.md` — final result and deliverables.

## 114.2 Update rules

Notes should be updated after meaningful state transitions, not every batch. They are summaries; immutable raw evidence stays in the ledger/experiment directories.

## 114.3 Handoff

A fresh agent should be able to reconstruct current state by reading in this order:

```text
requirements.md
notes/task.md
notes/progress.md
notes/validation.md
notes/decisions.md
exp/*/analysis.md for current top runs
research/synthesis.md
notes/final.md if completed
```

---

# 115. Observability, events, notifications, and walk-away behavior

## 115.1 Event stream

ML-Stack preserves upstream-style events and adds scientific events. Core event types include:

```text
processing
ready
assistant_chunk
assistant_message
assistant_stream_end
tool_call
tool_output
tool_log
tool_state_change
approval_required
turn_complete
error
interrupted
compacted
undo_complete
shutdown
requirements_locked
validation_locked
research_started
research_completed
hypothesis_created
experiment_queued
experiment_started
experiment_heartbeat
experiment_completed
experiment_failed
result_judged
version_promoted
benchmark_recorded
memory_card_proposed
memory_card_promoted
budget_warning
target_reached
finalization_started
finalization_completed
```

## 115.2 Heartbeats

Long jobs emit heartbeat/reconciliation state. A silent provider job does not automatically become `failed`; ML-Stack checks provider state before declaring it lost.

## 115.3 Notification gateways

Slack is required for ML Intern parity. Additional adapters can include email, Discord, Teams, webhook, or host-native notifications.

Useful automatic notification events default to:

```text
approval required
budget threshold
major unrecoverable error
target reached
final completion
```

Users can enable more frequent progress events.

## 115.4 Walk-away contract

A user may invoke `/ml-stack`, grant an autonomy budget, and leave. ML-Stack persists state continuously. If the host disconnects but remote jobs continue, a later session reconciles them.

---

# 116. Usage, budgets, approvals, and autonomous mode

ML-Stack maintains separate budgets for:

```text
LLM tokens/cost
web/research calls
CPU hours
GPU hours
provider monetary cost
experiment count
parallel jobs
wall time
artifact/storage size
```

Autonomous mode can auto-approve actions below configured thresholds. Any action exceeding a hard threshold pauses for approval. Destructive publication/deletion can remain approval-required regardless of budget.

Usage dashboards distinguish estimated, reserved, and actual spend.

---

# 117. Trace, trajectory, SFT, and analytics system

## 117.1 Traces

Each session can be serialized in a model/tool/event format suitable for replay and inspection. Trace sharing is private-by-default when remote storage is enabled.

## 117.2 Trajectory tags

Tags include upstream parity plus:

```text
project/task signature
requirements revision
validation protocol
experiment IDs
promoted version
compute provider
hardware
scientific outcome
technical outcome
memory-card references
```

## 117.3 SFT exports

The SFT builder can filter and transform trajectories for downstream research/training. It must obey privacy and licensing constraints and MUST NOT export secrets or prohibited held-out information.

## 117.4 KPIs

KPI aggregation can answer:

```text
experiments per project
promotion rate
technical failure rate
time-to-first-valid-baseline
time-to-best-run
research-to-experiment conversion rate
GPU utilization/cost efficiency
provider reliability
memory-card reuse rate
validation-regression rate
final audit failure rate
```

---

# 118. Backlog and self-improvement planning

The backlog is broader than software TODOs. It contains:

```text
unresolved scientific hypotheses
missing ablations
weak validation evidence
unstable seeds
failed technical runs worth retrying
provider/runtime issues
missing parity work
host adapter gaps
documentation gaps
benchmark regressions
memory contradictions
```

Prioritization uses:

```text
expected score/value gain
information gain
cost
risk
blocking power
confidence gap
user target urgency
requirements relevance
```

---

# 119. Cleanup, retention, and orphan reconciliation

ML-Stack periodically reconciles:

```text
remote jobs
sandboxes
local child processes
staged uploads
temporary worktrees
artifact transfers
locks
trace uploads
scheduled jobs
```

Cleanup supports dry-run and produces an audit record. Promoted artifacts, active jobs, and resources referenced by unfinished experiments cannot be deleted as orphans.

Retention policies can keep only top checkpoints while preserving lightweight manifests/metrics for every experiment.

---

# 120. Testing and parity release gates

A release calling itself ML Intern feature-parity MUST pass:

1. upstream tree/README/command/test scan against the pinned or configured snapshot;
2. capability manifest coverage with no unclassified functional surface;
3. unit tests for core runtime safeguards;
4. provider contract tests;
5. session persistence/resume tests;
6. tool-call malformed/dangling recovery tests;
7. context-compaction and loop-guard tests;
8. approval/budget tests;
9. auth/redaction tests;
10. research tool tests;
11. experiment ledger/provenance tests;
12. requirements compiler conflict tests;
13. deliverable adapter tests;
14. host installation smoke tests;
15. local and at least one remote execution integration test;
16. walk-away/resume fault-injection test;
17. memory privacy/leakage test;
18. cleanup/orphan test.

The parity report lives at:

```text
docs/parity/ml-intern.md
.ml-stack/parity/report.json
```

A newly discovered upstream capability is a release blocker until implemented or explicitly classified as presentation-only/host-provided with evidence.

---

# 121. Canonical implementation repository

Recommended repository structure:

```text
ml-stack/
├── README.md
├── LICENSE
├── NOTICE
├── pyproject.toml
├── uv.lock
├── setup
├── src/ml_stack/
│   ├── core/
│   ├── requirements/
│   ├── project/
│   ├── data/
│   ├── validation/
│   ├── research/
│   ├── experiments/
│   ├── evaluation/
│   ├── benchmark/
│   ├── memory/
│   ├── compute/
│   ├── providers/
│   ├── sandbox/
│   ├── jobs/
│   ├── artifacts/
│   ├── repositories/
│   ├── messaging/
│   ├── sessions/
│   ├── traces/
│   ├── usage/
│   ├── telemetry/
│   ├── security/
│   ├── parity/
│   ├── mcp/
│   ├── daemon/
│   └── cli/
├── skills-src/
├── adapters/
│   ├── claude-code/
│   ├── codex/
│   ├── chatgpt/
│   ├── opencode/
│   └── generic/
├── providers/
├── templates/
│   ├── requirements.md
│   ├── experiment/
│   ├── notes/
│   └── research/
├── schemas/
├── scripts/
├── tools/parity/
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   ├── replay/
│   ├── fault_injection/
│   └── host_smoke/
└── docs/
    ├── architecture/
    ├── providers/
    ├── hosts/
    ├── security/
    └── parity/
```

---

# 122. Implementation phases and no-feature-loss rule

## Phase A — portable core

Implement project discovery, requirements compiler, local execution, experiment ledger, validation lock, notes, version promotion, final audit, and basic Skill packaging.

## Phase B — research stack

Implement papers, web, docs/OpenAPI, GitHub/code research, source notebook, independent research worker, caching, and evidence schemas.

## Phase C — compute stack

Implement provider interface, HF Jobs/sandbox parity, local, Modal, Kaggle where allowed, SSH/Slurm, job schedules, artifacts, heartbeats, retries, cleanup.

## Phase D — runtime parity

Implement session persistence, context compaction, prompt caching, model switching/local endpoints, effort probing, tool recovery, doom loops, approvals, budgets, notifications, traces, usage, telemetry, SFT/KPI/backlog tools.

## Phase E — benchmarking and memory

Implement model/hardware/provider benchmark registries, knowledge cards, retrieval, cross-project learning, staleness/contradiction handling, privacy auditing.

## Phase F — host adapters

Ship Claude Code, Codex, ChatGPT, OpenCode, and generic adapters from one Skill source tree.

## Phase G — parity hardening

Run the upstream parity scanner, close every unclassified gap, add reliability tests for behavior implied by ML Intern tests, and publish the parity report.

**No-feature-loss rule:** implementation phases define order only. A v1.0 release that claims the full specification cannot omit a P1/P2 feature merely because earlier phases were enough for a demo.

---

# 123. Final acceptance criteria

ML-Stack v1.0 is complete when all of the following are true:

```text
[ ] `/ml-stack` can ingest an arbitrary ML project/challenge directory.
[ ] User requirements are persisted to requirements.md and compiled into a versioned lock.
[ ] Output filenames/artifact types are requirements-driven, not hardcoded.
[ ] exp/* is the canonical experiment workspace and every run has provenance.
[ ] train/validation/test boundaries can be encoded and audited.
[ ] Research can use papers, citation graphs, full text, web, docs/OpenAPI, GitHub, datasets, and model resources.
[ ] Research findings become testable hypotheses with evidence references.
[ ] CPU/GPU/resource requirements are inferred and provider selection is pluggable.
[ ] Local, HF Jobs, HF sandbox, and at least one additional remote provider work through the same job contract.
[ ] Experiments record quality, runtime, memory, failures, and artifacts.
[ ] Baselines, ablations, hyperparameter search, seed tests, and ensembles are supported.
[ ] Result judging separates technical failure from scientific evidence.
[ ] Promoted versions are immutable and reproducible.
[ ] Final deliverables are materialized and validated from the active requirements contract.
[ ] Research, benchmark, and notes directories provide a human-readable scientific record.
[ ] Model/hardware/provider benchmarking is first-class.
[ ] Project/workspace/global learning stores reusable non-sensitive lessons and retrieves them for future work.
[ ] Cross-project memory passes anti-leakage/privacy audits.
[ ] Session persistence/resume, interrupt, clear, context compaction, and trace export work.
[ ] Model switching/local OpenAI-compatible endpoints/reasoning-effort probing have parity equivalents.
[ ] Doom-loop, polling-loop, malformed-tool, dangling-tool, no-tool-continuation, and compaction-loop protections work.
[ ] Approvals, auto-approval/autonomy, cost estimates, usage thresholds, and budgets work.
[ ] Slack notification parity works and notification gateways are extensible.
[ ] HF paper/docs/dataset/repository/jobs/sandbox capabilities from the pinned ML Intern snapshot are mapped and tested.
[ ] Scheduled job operations are implemented.
[ ] Hub branch/tag/PR/repo operations are implemented.
[ ] Dataset staging/upload is implemented for remote execution.
[ ] Trackio-compatible experiment tracking integration exists where applicable.
[ ] Trace visibility is private-by-default and controllable.
[ ] KPI aggregation/scheduling, SFT export/tagging, backlog prioritization, and orphan cleanup exist.
[ ] The upstream parity scanner reports zero unclassified functional features.
[ ] Claude Code, Codex, ChatGPT, OpenCode, and generic host installation paths exist.
[ ] Installation uses one source-of-truth Skill/runtime bundle.
[ ] A walk-away run can survive host/process interruption and resume/reconcile safely.
[ ] The final report distinguishes measured, externally observed, literature evidence, estimated, hypothesis, and unknown claims.
```

The product is successful when a user can give an ML project plus its requirements, invoke **`/ml-stack`**, leave, and later return to a reproducible scientific record and the strongest legitimate deliverables ML-Stack could establish within the allowed evidence, compute, time, and budget — while the system becomes better at planning future ML work from the reusable lessons of past work without learning forbidden answers or pretending guesses were measurements.

---

# Appendix A. Canonical default `requirements.md`

```markdown
# ML-Stack Requirements

## User Directive
<captured from the user; preserve intent and important wording>

## Objective
Achieve the strongest legitimate result supported by the active project rules and available evidence.

## Mode
- auto-detect

## Inputs
- auto-discover from project

## Required Deliverables
- discover from user/project/platform; do not assume filenames

## Runtime Interface
- discover if present

## Metric / Success Criteria
- primary metric: discover
- direction: discover
- target: user-specified if present

## Validation Requirements
- use only data legally available for model development
- design the split to mimic evaluation
- lock protocol before broad model search
- fit learned preprocessing only inside allowed training boundaries

## Experimentation Policy
- create exp/*
- establish multiple meaningful baselines when useful
- test materially different hypotheses
- run ablations for promising components
- test stability across seeds/splits when practical
- test ensembles when errors are complementary
- do not promote unmeasured intuition over measured evidence

## Held-out / Test Isolation
- compile from active project rules
- default to frozen held-out inference for benchmark/challenge tasks unless the task explicitly allows transductive/joint methods

## Development Compute
- auto-detect local capabilities
- remote providers may be used within budget and policy

## Final Compute
- compile from platform/project rules

## Network Policy
- development research: allowed when host/user/project permits
- training/inference: compile from project rules

## External Data / Pretrained Assets
- compile from project rules

## Allowed Methods
- legitimate ML/statistical/scientific methods consistent with the project

## Prohibited Methods
- leakage
- hidden-answer ingestion
- fabricated measurements
- test-specific hardcoding unless the task explicitly defines a deterministic non-ML rule system

## Reproducibility
- record seeds, environment, code hash, data hash, validation protocol, and run configuration

## Research Policy
- use papers, citations, docs, web, GitHub/code, model cards, dataset cards, and benchmarks when useful
- save durable notes under research/

## Benchmarking Policy
- record task quality and resource use for meaningful experiments
- maintain model/hardware/provider empirical records

## Notes / Reporting
- maintain notes/task.md
- maintain notes/data.md
- maintain notes/validation.md
- maintain notes/decisions.md
- maintain notes/failures.md
- maintain notes/ideas.md
- maintain notes/progress.md
- write notes/final.md

## Cross-project Learning
- reusable non-sensitive distilled lessons: allowed by default
- raw held-out/test examples: prohibited by default
- secrets/private raw data: prohibited by default

## Budgets and Approvals
- obey configured autonomy, compute, cost, experiment-count, and destructive-action limits
```

---

# Appendix B. Canonical experiment `hypothesis.md`

```markdown
# <Experiment ID>: <Title>

## Hypothesis
<one clear scientific claim>

## Mechanism
<why this could improve the objective>

## Evidence
- <paper/source/previous run/knowledge card>

## Change vs Parent
<what changes and what remains controlled>

## Expected Outcome
<metric/resource expectation with uncertainty>

## Risks
<overfit, compute, implementation, leakage, instability>

## Success Gate
<predeclared comparison rule>
```

---

# Appendix C. Canonical experiment `analysis.md`

```markdown
# <Experiment ID>: Result

## Status
- technical:
- scientific:

## Measurements
- validation:
- train diagnostic:
- runtime:
- memory:
- throughput:
- cost:

## Comparison
<against parent/baseline under same validation protocol>

## Diagnostics
<errors, instability, resource behavior>

## Decision
PROMOTE | REJECT | INCONCLUSIVE | RETRY_TECHNICAL | ROBUSTNESS_REQUIRED | INVALID_COMPARISON

## Why
<evidence-based reason>

## Next Hypotheses
- ...
```

---

# Appendix D. ML-Stack product invariant

**ML-Stack is a portable autonomous ML research stack, not another chat UI.** It takes the user's requirements as the contract, uses the host agent as the visible intelligence, supplies the full research/experiment/compute/memory/tooling substrate, preserves the useful functional surface of ML Intern as Skills/plugins/tools, keeps durable scientific notes, learns reusable lessons from repeated model training, and returns verified requirements-driven deliverables rather than assuming one competition template.

