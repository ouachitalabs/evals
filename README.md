# Invoice extraction evals

Five [Harbor](https://docs.harborframework.com/) tasks evaluate one small AI feature: **invoice image → one model call → raw answer → scores**. Each task is one real Portuguese document from [InvoicesReceiptsPT](https://huggingface.co/datasets/Francisco-Cruz/InvoicesReceiptsPT).

## Run one document

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), start Docker, then:

```sh
uv sync
export OPENROUTER_API_KEY=YOUR_KEY
uv run harbor run --yes --path tasks/ \
  --agent evals.invoice_agent:InvoiceExtractorAgent \
  --model openrouter/deepseek/deepseek-v4.1-flash
```

For all five, use `--path tasks -n 2`. Both extraction and summary judging use DeepSeek V4.1 Flash through OpenRouter; these are separate calls.

## Follow one eval

Open [the Easy Style task](tasks/invoice-easy-style/). It follows the [Harbor task layout](https://docs.harborframework.com/core-concepts/tasks/overview):

```text
invoice-easy-style/
├── instruction.md              # Prompt: return seven JSON string fields
├── task.toml                   # Timeouts, containers, copied artifacts
├── environment/
│   ├── Dockerfile
│   └── invoice.jpg             # Model input
├── solution/
│   ├── solve.sh                # Oracle writes a known answer; no extraction call
│   └── response.json
└── tests/
    ├── Dockerfile              # Separate verifier container
    ├── test.sh                 # Prepares summary text, runs Rewardkit
    ├── expected.json           # Six labeled facts + example summary
    ├── json_validity/check.py  # JSON shape and field formats
    ├── field_accuracy/check.py # Six factual comparisons
    └── summary/judge.toml      # LLM rubric: useful description, no inventions
```

The shared [runner](src/evals/invoice_agent.py) sends the prompt and image in **one request**, with reasoning enabled. It saves assistant text unchanged to `/app/response.json`, even if that text is malformed JSON, fenced Markdown, or empty. There is no JSON mode, answer parsing, repair, or automatic retry. The SDK unwraps the API envelope; only the verifier parses the answer itself.

Harbor copies the image and answer into the verifier container. Python grades format and facts. The summary judge sees **only the image and extracted summary**, not the other fields or expected answer. Both rubric questions must pass. The reference summary is an example, not an exact-match target.

## Read three scores

Run `uv run harbor view jobs` and open a trial.

| Score | Meaning | What it does not establish |
| --- | --- | --- |
| `json_validity` | 1 if the answer has exactly seven nonempty strings with the required date, tax-ID, and money formats; otherwise 0. | Whether the facts are correct. |
| `field_accuracy` | Fraction of the six factual fields that match. | Whether the whole output meets the schema or the summary is true. |
| `summary` | 1 if both LLM rubric questions pass; otherwise 0. | A guarantee of correctness; inspect the judge's reasons. |

There is no blended overall score. Invalid JSON gets zero factual credit. A parseable answer can earn factual credit while failing the schema.

**Matching policy:** seller names must match completely after ignoring case, accents, and repeated/outer whitespace. Invoice numbers ignore case and repeated/outer whitespace, but preserve punctuation. Tax IDs and dates match exactly. Amounts require two decimal places and the correct numeric value. Unlisted seller aliases or legal-name variants can fail; review those failures against the image before expanding accepted answers.

In each trial's logs:

- `agent/response.json`: unchanged assistant text being graded.
- `agent/api-response.json`: complete API response body, including returned reasoning, finish reason, and usage. Available for model runs, not oracle runs.
- `agent/trajectory.json`: prompt, image attachment, and answer in Harbor's viewer.
- `verifier/reward.json`: the three scores.
- `verifier/reward-details.json`: individual checks and judge explanations.

## A concrete failure

The [Easy Style image](tasks/invoice-easy-style/environment/invoice.jpg) shows ten card holders totaling **€12.00**. This [deliberately wrong submission](examples/grader-checks/wrong-total.json) is valid JSON:

```json
{
  "seller_name": "easy style",
  "seller_tax_id": "240740831",
  "invoice_date": "2019-05-29",
  "invoice_number": "FAC 1101/00004180",
  "total": "120.00",
  "tax_amount": "2.24",
  "order_summary": "Ten card holders."
}
```

The `total` check fails: `120.00` ≠ `12.00`. Five of six facts still match. The [actual verifier result](examples/grader-checks/wrong-total-result.json) was `json_validity: 1`, `field_accuracy: 0.8333` (5/6, rounded), and `summary: 1`. The judge accepted the item type and quantity visible in the image. The format passing does not make the extracted total correct.

## Check the graders

```sh
uv run python scripts/check_graders.py
```

This runs **real Harbor trials** with the oracle submitting saved answers: five correct references, plus fenced JSON, an empty answer, a wrong total, an invented summary, the buyer's tax ID, extra seller-name text, changed invoice punctuation, and acceptable formatting differences. The extractor is bypassed; the real verifier and LLM judge run. Docker and the API key are required, and judging incurs API usage.

[The cases](examples/grader-checks/cases.json) state expected scores and which factual checks must fail. The script exits unsuccessfully on mismatches or trial errors and saves `jobs/grader-checks-*/grader-checks.json`; open the corresponding trial to understand a failure. LLM judgments can vary, so a mismatch warrants reading the reasoning, not blindly changing the expectation.

## Try a change

Edit a prompt or change `--model`, rerun the same documents, and compare each score and failure explanation. The five documents cover a short purchase, reduced VAT, buyer-versus-seller information, zero VAT, and multiple items. Keep new documents aside if you optimize against these five.

Each task's `SOURCE.md` links its image and annotation at a fixed Hugging Face revision. Images are bundled for repeatable runs; the full dataset is not downloaded. The [original dataset record](https://zenodo.org/records/6371710) licenses the collection CC BY 4.0. Five documents are a teaching example, not a production accuracy estimate.
