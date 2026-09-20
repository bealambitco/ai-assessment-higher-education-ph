# Arm G: low-resource models — configurations fixed before collection

Fixed on September 20, 2026. Open-weight models in the 8B–30B range answer the same 24 cases with the same
supplied excerpt and the same required JSON format as the primary study. They are reached through OpenRouter,
a hosted aggregator, not run offline.

## Models

| Label | OpenRouter model id | Weights | Why it is here | Local footprint for comparison |
|---|---|---|---|---|
| `gptoss20b` | `openai/gpt-oss-20b` | open | Cheapest of the group; runs on a 16 GB machine | about 14 GB (Ollama `gpt-oss:20b`) |
| `qwen3-30b-a3b` | `qwen/qwen3-30b-a3b-instruct-2507` | open | Mixture-of-experts: the fastest realistic self-hosted option | about 19 GB (`qwen3:30b`) |
| `gemma3-12b` | `google/gemma-3-12b-it` | open | The floor case: fits comfortably in 16 GB | about 8 GB (`gemma3:12b`) |

Settings, identical across the three: temperature 0, max output 4000 tokens, one request per case, no tools,
no web search, no follow-up, first reply kept. Structured-output enforcement is **not** used, because the
primary study asked for JSON in the prompt only; enforcing a schema here would make format failures
incomparable with the rest of the study. Format failures are a result, not a problem to be engineered away.

Paid endpoints are used rather than the free variants: free endpoints on these models expose different
parameter support and a 50-request daily cap, which would confound the comparison. At listed prices a full
24-case run costs well under one US cent per model; the recorded cost comes from OpenRouter's own figure for
each request.

## Two prompt conditions

The models were first sent a prompt written for this arm: the same case, the same excerpt and the same
required schema as the primary comparison, but with its own wording and an added instruction to answer only
from the evidence given. That prompt is about 77 percent similar to the one the primary configurations
received, so a format difference between the two could in principle come from the wording rather than the
model.

Because the arm costs well under a cent per model, the same 24 cases were also sent **the study's own frozen
prompt, unchanged**, byte for byte as the primary configurations received it. Both conditions are reported:
[summary.csv](summary.csv) for the prompt written for this arm and
[summary-matched-prompt.csv](summary-matched-prompt.csv) for the frozen one.

The wording matters enough to be worth reporting. Under the frozen prompt, gpt-oss-20b produced valid
structure in all 24 answers instead of 22, while qwen3-30b-a3b fell from 21 to 20 and gemma-3-12b rose from
20 to 21; across the three models, 65 of 72 answers were valid instead of 63. In the other direction, the
frozen prompt drew more quotations (232 against 203) and more quotations that are not in the supplied
excerpt (27 against 11). No claim in the paper rests on one configuration's count in one condition.

## What this arm can and cannot establish

It can establish how models a school could legally self-host handle the same rule-based requests: whether
they produce the required structure, whether their quotations exist in the supplied excerpt, whether their
recomputations are right, and what the checks do with their answers. Answers are scored by the researcher
under the unchanged keys, so this is a correctness comparison and not only a format one.

It cannot establish offline operation, privacy or data sovereignty: prompts still leave the country and
reach third-party infrastructure. It cannot establish latency or hardware feasibility on a school's own
machine. The provider serves these models at higher precision than a school running a quantized copy would,
so the results are an upper bound on what self-hosting would achieve.

## Optional local spot-check

Two cases (W2-07, numeric, and W1-03, judgment) may be run locally on one model through Ollama, to bound the
gap between a hosted copy and a quantized local copy. That is a limitation check on this arm, not a fourth
configuration, and it is reported as such. It requires installing Ollama and pulling one model of about 8 GB;
everything else in this arm needs no installation.

## Wording for the paper

> The low-resource arm was run through a hosted aggregator using open-weight models in the 8B–30B range,
> that is, models whose weights are publicly downloadable and that fit on commodity hardware. It isolates
> model capability under a constrained budget. It is not an offline deployment, so no privacy, latency or
> hardware claim follows; providers serve these models at higher precision than a self-hosting school would
> use, so these figures are an upper bound on what such a school could achieve.
