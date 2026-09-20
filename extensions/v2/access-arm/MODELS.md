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
