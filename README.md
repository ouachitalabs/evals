# Evaluate the whole feature

A companion exercise for John McCrary's **AI in the Rock** talk. One
[Harbor task](tasks/algebra-tutor/) asks an AI tutor to respond to a student's
mistake in `3(x - 2) = 12`. Harbor runs the agent and a separate verifier, then
reports factual correctness, teaching quality, and an overall reward.

| Reward | Source | Meaning |
| --- | --- | --- |
| `correctness` | [Programmatic Rewardkit criterion](tasks/algebra-tutor/tests/shared_math.py) | The structured answer and the reply's explicit `x = ...` both solve the original equation. |
| `teaching_quality` | [Rewardkit judge rubric](tasks/algebra-tutor/tests/live/teaching_quality/judge.toml) | DeepSeek V4.1 Flash checks error diagnosis, reasoning, clarity, and a self-check. |
| `reward` | [Rewardkit aggregation](tasks/algebra-tutor/tests/live/reward.toml) | Live success requires a weighted score of at least 0.75. Because a wrong answer can reach at most 0.5, correctness gates success. Offline reward equals correctness. |

The task layout follows [Terminal-Bench](https://github.com/harbor-framework/terminal-bench):
`task.toml`, `instruction.md`, `environment/`, `tests/`, and `solution/`.
Harbor collects `/app/response.json`, starts the verifier container, runs
[`tests/test.sh`](tasks/algebra-tutor/tests/test.sh), and reads Rewardkit's
`/logs/verifier/reward.json`. The teaching rubric is available only in the
verifier container. The agent container has no network access.

## Run the task offline

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and start
Docker. From this repository's root:

```sh
uvx --from harbor==0.23.0 harbor run --yes --path tasks/algebra-tutor --agent oracle
```

The oracle is the reference solution. The expected Harbor rewards are
`correctness=1.0` and `reward=1.0`. No API key is needed. To evaluate another
agent, replace `oracle` and add its model and authentication as required by
Harbor:

```sh
uvx --from harbor==0.23.0 harbor run --yes --path tasks/algebra-tutor --agent codex --model YOUR_MODEL
```

Harbor writes the response under `jobs/<job>/<trial>/artifacts/app/response.json`
and scores under `verifier/reward.json` and `verifier/reward-details.json`. Run
`uvx --from harbor==0.23.0 harbor view jobs` to inspect the trial.

## Run with the live teaching judge

For a local demo, put a single `OPENROUTER_API_KEY=...` assignment in
`~/.secrets` and run:

```sh
uv run python scripts/run_live.py
```

The small launcher reads the key privately and starts **Harbor** with its
Terminus-2 agent and DeepSeek V4.1 Flash model. The same model grades teaching
quality through Rewardkit. Harbor resolves the key into the verifier's
environment at run time; the
task config retains only an environment-variable template. The key is not
placed in the agent container, image, command arguments, or reward files. The
verifier has internet access to call OpenRouter. The default agent run allows
up to eight turns to keep a demo bounded. To use another agent, pass its
Harbor arguments through the launcher:

```sh
uv run python scripts/run_live.py --agent codex --model YOUR_MODEL
```

If your key is already exported by a secret manager, run Harbor directly:

```sh
EVAL_JUDGE_MODE=live uvx --from harbor==0.23.0 harbor run --yes --path tasks/algebra-tutor --agent oracle
```

The model is [DeepSeek V4.1 Flash](https://openrouter.ai/deepseek/deepseek-v4.1-flash)
through OpenRouter. Rewardkit sends the response and the four binary criteria
to the judge in one call and records criterion scores and reasoning in
`reward-details.json`. A judge rating is a **proxy for teaching quality**, not
proof that a student learned. Using the same model to answer and judge is
convenient for this demo but warrants independent teacher calibration. The
reply and rubric leave the verifier for OpenRouter, so use only data you may
share.

## Inspect the grader's limits

The four [example responses](examples/) show a good lesson, a correct answer
with poor teaching, a fluent wrong answer, and a reply whose prose contradicts
its structured answer. The correctness check rejects the latter two. The live
rubric can distinguish the first two.

The deterministic check is intentionally narrow: it reads the structured
answer and one explicit conclusion in the reply. A misleading explanation can
still pass that check. Before using live scores to compare models, collect real
tutor interactions with consent, have teachers label a small sample, compare
the judge's scores to those labels, and repeat judgments to measure stability.
Keep examples where the judge and teachers disagree.

To adapt this task, replace the scenario in
[`instruction.md`](tasks/algebra-tutor/instruction.md), update the independent
truth check in [`shared_math.py`](tasks/algebra-tutor/tests/shared_math.py), and
revise the judge criteria and examples. For a refund assistant, verify the
database refund state before scoring the helpfulness of its message. For code
generation, check behavior with tests and review quality and security
separately.
