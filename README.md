# Evals

One [Harbor](https://docs.harborframework.com/) task tests an AI algebra tutor on both **math correctness** and **teaching quality**. [Rewardkit](https://docs.harborframework.com/core-concepts/rewardkit/quick-start) checks the answer deterministically, uses DeepSeek V4.1 Flash to judge the explanation, and reports separate scores. Incorrect math cannot earn an overall pass.

## Explore

- [`instruction.md`](tasks/algebra-tutor/instruction.md): what the tutor sees.
- [`tests/shared_math.py`](tasks/algebra-tutor/tests/shared_math.py): the factual check.
- [`tests/live/teaching_quality/judge.toml`](tasks/algebra-tutor/tests/live/teaching_quality/judge.toml): the teaching rubric.
- [`tests/live/reward.toml`](tasks/algebra-tutor/tests/live/reward.toml): the overall pass rule.
- [`examples/`](examples/): good, terse, wrong, and contradictory replies.

To adapt it, change the student prompt, factual check, and rubric together. A judge score is a proxy for teaching quality, not proof of learning.

## Run

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and start Docker. From the repo root, run the reference solution offline:

```sh
uvx --from harbor==0.23.0 harbor run --yes --path tasks/algebra-tutor --agent oracle
```

Run DeepSeek V4.1 Flash as both tutor agent and live judge:

```sh
export OPENROUTER_API_KEY=YOUR_KEY && \
EVAL_JUDGE_MODE=live uvx --from harbor==0.23.0 harbor run --yes \
  --path tasks/algebra-tutor \
  --agent terminus-2 \
  --model openrouter/deepseek/deepseek-v4.1-flash \
  --ak max_turns=8 \
  --ak record_terminal_session=false
```

Results are in `jobs/`. Open them with `uvx --from harbor==0.23.0 harbor view jobs`.
