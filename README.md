# Evaluate the whole feature

This is the companion exercise for John McCrary's **AI in the Rock** talk. One
[Harbor task](tasks/algebra-tutor/) asks an AI tutor to respond to a student's
mistake in `3(x - 2) = 12`. Its output is a student-facing explanation plus a
structured final answer. The two parts are graded separately:

| Dimension | Check | Meaning |
| --- | --- | --- |
| Math correctness | Deterministic | The JSON answer and the reply's explicit `x = ...` both solve the original equation. |
| Teaching quality | Optional OpenRouter LLM judge | A 0–4 rubric scores error diagnosis, reasoning, clarity, and a useful self-check. |
| Overall live reward | `correctness × teaching_score / 4` | A fluent but wrong reply scores zero. |

The offline Harbor reward is **correctness only**. Its `teaching_score` is
unjudged, not zero. See the transparent [grader](tasks/algebra-tutor/tests/grade.py)
and [rubric](tasks/algebra-tutor/tests/rubric.md).

## Run without an API key

Requires Python 3.11 or newer. From this repository's root:

```sh
python3 tasks/algebra-tutor/tests/grade.py --response examples/good.json
python3 tasks/algebra-tutor/tests/grade.py --response examples/correct-but-poor-teaching.json
python3 tasks/algebra-tutor/tests/grade.py --response examples/fluent-but-wrong.json
python3 tasks/algebra-tutor/tests/grade.py --response examples/metadata-claim-only.json
```

The first two pass math correctness, even though one is a poor lesson. The
fluent wrong answer fails, as does a reply that claims `x = 5` while its JSON
metadata claims 6. These contrasts show why one score is not enough.

## Run the Harbor task

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and start
Docker. From the repository root:

```sh
uv tool install harbor==0.23.0
harbor run --path tasks/algebra-tutor --agent oracle --artifact /app/response.json
```

The oracle creates a worked tutor response, then Harbor executes the verifier.
It should earn `reward=1.0` and `correctness=1.0`. Harbor writes detailed
`score.json` and `reward.json` in the job's trial verifier logs. To evaluate your
own AI agent instead, select an [agent supported by Harbor](https://harborframework.com/docs)
and its model, for example:

```sh
harbor run --path tasks/algebra-tutor --agent codex --model YOUR_MODEL --artifact /app/response.json
```

Agent authentication and model selection are separate from the grader. The
task's Docker container has no network access, and the offline verifier needs
no credential.

## Add the live teaching judge

Set `OPENROUTER_API_KEY` in your shell environment using your own secret
manager. Never put it in `task.toml`, a command argument, or a committed file.
Then run the same grader on a local response:

```sh
python3 tasks/algebra-tutor/tests/grade.py --response examples/good.json --live
python3 tasks/algebra-tutor/tests/grade.py --response examples/correct-but-poor-teaching.json --live
python3 tasks/algebra-tutor/tests/grade.py --response examples/fluent-but-wrong.json --live
```

The default judge is `openai/gpt-4.1-nano` on OpenRouter. Override it with
`--model SLUG`. Each command makes one small request with a 180-token response
cap. The grader requests structured JSON, validates the returned 0–4 integer,
and fails rather than silently substituting a score if the service is
unavailable. It sends the student reply and rubric to OpenRouter, so use only
data you are allowed to share. The model's reasoning and scores may vary.

For a Harbor-generated response, the `--artifact` option downloads the response
into the trial's `artifacts` directory. Pass that file to the grader with
`--response`. The live call runs on the host so the task environment remains
offline and the judge credential never enters the container.

## What this example does and does not measure

The math check is unusually crisp: the original equation has a known answer.
It still only reads the structured answer and one explicit conclusion in the
reply. A misleading explanation can pass that check. The rubric attempts to
measure explanation quality, but its score is a **proxy**, not evidence that a
student learned. A teacher or student outcome is the stronger signal. Before
using the judge to compare models, collect real tutor interactions with consent,
have teachers label a small sample, compare judge scores to those labels, and
repeat judgments to see how stable they are. Keep examples of disagreements.

The pattern generalizes: capture real feature traces, check the parts with known
truth (including tools and state changes), then use a calibrated rubric for
outcomes that need human judgment. For a refund assistant, verify the database
refund state before scoring how helpful the message sounds. For code generation,
tests can check behavior while a separate review checks quality and security.

To adapt this task, replace the scenario in
[`instruction.md`](tasks/algebra-tutor/instruction.md), update the independent
truth check in [`grade.py`](tasks/algebra-tutor/tests/grade.py), replace the
teaching rubric, and write contrasting examples like these four. Keep the
dimensions visible and ensure that a failed factual check gates overall success.
