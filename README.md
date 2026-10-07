# Local Multi-Agent Trading Workstation

A local-first, model-agnostic research and day-trading workstation.

## Design principles

- Statistical models produce trade probabilities; LLMs do not replace the quant engine.
- Risk rules are deterministic and cannot be overridden by an LLM.
- Paid agents are event-driven and wake only when a candidate earns deeper analysis.
- Model vendors are swappable behind adapters.
- API spend is part of system P&L and is governed by a rolling monthly budget.
- Every agent must eventually justify its cost with measurable incremental value.

## Initial architecture

```text
Market data
   |
   v
Feature engine -> Quant model -> Candidate router
                                |      |      |
                                v      v      v
                              News   Critic  Regime
                                \      |      /
                                 Coordinator
                                      |
                                      v
                                  Risk engine
                                      |
                                      v
                               TRADE / WAIT / REJECT
```

## Repository layout

```text
backend/
  app/
    config.py
    cost_budget.py
    trigger_policy.py
  tests/
frontend/
docs/
```

## V1 thresholds

- < 60%: discard
- 60-68%: monitor locally
- >= 68%: allow low-cost research/catalyst call
- >= 74%: allow premium reasoning call
- >= 80%: allow independent critic call
- Above the normal daily API allowance, rollover funds require stricter thresholds.

## API budget policy

- Absolute monthly cap: **$100**
- Normal daily target: **$5 per trading day**
- Unused daily allowance rolls forward.
- A later day may exceed $5 only by consuming previously banked allowance.
- Once the normal $5 daily allowance is exhausted, rollover spending is gated by stricter candidate-confidence thresholds.
- When the monthly cap is exhausted, discretionary paid-agent calls stop.

The budget engine lives in `backend/app/cost_budget.py` and is deliberately independent of any model vendor.
