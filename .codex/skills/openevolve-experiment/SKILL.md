---
name: openevolve-experiment
description: Create or improve OpenEvolve experiments in this repo by generating or editing the required experiment files (initial_program.py or initial_text.txt, config.yaml, evaluator.py). Use when a user asks to set up a new OpenEvolve experiment, tune an existing experiment, or refine evaluation metrics, prompts, and evolution settings.
---

# Openevolve Experiment

## Overview

Create or upgrade OpenEvolve experiments for strong, reproducible optimization results.

Your primary goal is not just to produce files, but to produce an experiment setup that:
- ranks candidates correctly (clear fitness metric)
- explores effectively (prompt + diversity settings)
- evaluates reliably (deterministic, robust evaluator)
- can be tuned quickly through short validation runs

## Workflow

Decide which path applies, then follow the steps.

### 1. New Experiment
- Use when the user wants to create a new experiment from scratch.

### 2. Improve Existing Experiment
- Use when the user wants to modify or extend an existing experiment.

## Required Local References

Always read these files before drafting or editing:
- `docs/openevolve/examples/README.md`
- `docs/openevolve/openevolve_config_hyperparameters_cheat_sheet.txt`
- `docs/openevolve/examples/signal_processing/config.yaml`
- `docs/openevolve/examples/signal_processing/evaluator.py`
- `docs/openevolve/examples/signal_processing/initial_program.py`

Use additional examples only if the requested domain is closer to another example.

## Non-Negotiable Quality Gates

Before finalizing any experiment, enforce all of these:

1. Evaluator returns a numeric `combined_score` where higher is better.
2. `early_stopping_metric` points to a metric actually returned by evaluator (prefer `combined_score`).
3. `cascade_evaluation` is `false` unless `evaluate_stage1` exists (and ideally `evaluate_stage2` / `evaluate_stage3`).
4. `file_suffix`, language, and input artifact type are consistent (`.py`, `.rs`, `.txt`, etc).
5. `diff_based_evolution` matches mutation mode:
   - `true` for targeted edits in evolvable blocks.
   - `false` for text experiments or broad rewrites.
6. Evaluator is deterministic (fixed seeds, stable test cases, bounded runtime).

If any gate fails, fix it before proposing further tuning.

## New Experiment Workflow

### Gather Inputs
Ask for missing essentials, but do not require the user to provide the cheat sheet path (load it directly).
- Experiment goal and success criteria (metrics, constraints, tradeoffs)
- Target language and runtime constraints (CPU/GPU, time limits, memory)
- Initial program or initial text path, or a description to create it from scratch
- Preferred output location (default to a new folder under `examples/`)
- LLM provider preferences if any (model, api_base)

### Pick Baseline Reference
- Choose the closest existing example in `examples/` by domain and modality (code vs text).
- Reuse its structure as the scaffold before introducing custom logic.

### Create or Update Initial Candidate (`initial_program.py` or text file)
- Follow the pattern of the chosen baseline example.
- For code experiments, wrap evolvable regions with:
  - `# EVOLVE-BLOCK-START`
  - `# EVOLVE-BLOCK-END`
- Keep non-evolvable scaffolding stable and evolvable code focused.
- For text experiments, use a text file (commonly `initial_prompt.txt`) and set `file_suffix: ".txt"` plus `diff_based_evolution: false`.

### Create `evaluator.py`
- Load the candidate program via `importlib` (see example).
- Run deterministic evaluations (seed randomness if used).
- Return a metrics dictionary with a numeric `combined_score` (primary optimization target).
- Include additional diagnostic metrics, but make sure they align with optimization intent.
- Ensure timeout behavior is explicit and evaluator failures return low fitness, not ambiguous scores.
- If using cascade evaluation, define stage functions correctly (`evaluate_stage1`, optional `evaluate_stage2`, optional `evaluate_stage3`); otherwise set `cascade_evaluation: false`.

### Create `config.yaml`
- Use the cheat sheet to place parameters in the correct sections.
- Set `prompt.system_message` with domain-specific role, allowed moves, forbidden changes, and success criteria.
- Ensure evaluator-related config matches evaluator implementation exactly.
- Keep `diff_based_evolution` consistent with EVOLVE-BLOCK usage and mutation type.
- Prefer modern `llm.models` array for new configs (legacy `primary_model` fields only for compatibility).
- Do not rely on known non-implemented fields for enforcement (`evaluator.memory_limit_mb`, `evaluator.cpu_limit`, `evaluator.distributed`, prompt meta-prompting fields). Implement constraints in evaluator code instead.

### Initial Tuning Defaults
For a first validation run, use conservative defaults:
- `max_iterations`: 30-100
- `checkpoint_interval`: 5-20
- `prompt.num_top_programs`: 2-4
- `prompt.num_diverse_programs`: 2-5
- `prompt.include_artifacts`: true
- `database.feature_dimensions`: start with built-ins, add custom metrics only when meaningful
- `evaluator.parallel_evaluations`: match available resources and evaluator cost

### Final Checks
- Verify the quality gates section above.
- Verify `combined_score` directionality (higher should mean better outcome).
- Ensure paths in any run instructions are correct.
- Provide at least one short smoke-test run command, e.g.:
  - `python openevolve-run.py <initial_program.py> <evaluator.py> --config <config.yaml> --iterations 50`
- If this is a costly evaluator, also provide a cheaper validation command with fewer iterations.

## Improve Existing Experiment Workflow

### Gather Inputs
- Experiment folder and files to modify.
- Desired changes (metrics, prompt, constraints, runtime, model settings).

### Diagnose Before Editing
- Read current `config.yaml`, `evaluator.py`, and initial artifact.
- Identify primary bottleneck first:
  - weak/unstable evaluator
  - misaligned `combined_score`
  - poor system message
  - too little diversity
  - expensive evaluation causing low iteration throughput
- State the bottleneck and propose targeted edits before broad changes.

### Update Files
- Read the existing `initial_program.py`/`initial_text.txt`, `evaluator.py`, and `config.yaml`.
- Keep evaluator metrics consistent with config references (early stopping, feature dimensions, thresholds).
- Upgrade `prompt.system_message` using the README iterative method:
  - role and context
  - concrete optimization opportunities
  - hard constraints
  - anti-patterns from observed failures/artifacts
- Preserve model/provider settings unless user requests a change.

### Validate
- Run a short evolution sanity check when possible (20-50 iterations).
- Inspect logs/artifacts for:
  - parse failures (diff mode issues)
  - timeout-heavy evaluations
  - repeated low-diversity mutations
  - missing or flat `combined_score` improvement
- If execution is not possible, provide a run command plus explicit risk list.

## Optimization Heuristics

Apply these by default when searching for better outcomes:
- If diff parsing or fragile edits appear, switch `diff_based_evolution: false`.
- If evaluator is slow, use cascade stages or smaller early-stage workloads.
- If population collapses to similar solutions, increase diversity pressure (`num_diverse_programs`, template stochasticity, broader feature dimensions).
- If evolution is noisy, tighten determinism and simplify objective mixing.
- If the objective is multi-metric, keep `combined_score` interpretable and stable.

## Deliverable Standard

Every response using this skill should include:
1. What changed and why it improves results.
2. The exact files touched.
3. A run command for quick validation.
4. Remaining risks or assumptions.
