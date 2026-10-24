# API and native interchange

```python
from voltvar.cli import load_case
from voltvar.studies import run
model = load_case("example:industrial")
result = run(model, "analyze")
```

Actions: analyze, optimize, local, time_series, uncertainty.

Example options: `optimize`: {"q_levels":3,"max_candidates":2000}. `local`: {"max_rounds":40,"target_pu":1,"deadband_pu":0.01}. `time_series`: {"mode":"coordinated"} or {"mode":"local"}. `uncertainty`: {"scales":[0.5,0.8,1]}.

The packaged JSON reference is the native model schema. Each numerical submodule also exposes ordinary Python functions. CLI `--options` accepts JSON; `--output` saves the complete report. A result fingerprint identifies exact model/options/version, not professional approval. Imported models are validated on study execution; exports are disabled after edits and failed calculations.

HTTP `GET /api/examples`, `GET /api/example?name=industrial`, `POST /api/study` with `{"network":model,"action":"analyze","options":{}}`. The historical envelope name network contains the entire native study model. `POST /api/import` accepts `{"text":"JSON model"}`. Body limit 2 MB, same-origin browser checks, allowlisted static assets and CSP. No arbitrary file path or code execution API.

`network` uses GridFlow native JSON (schema_version 1). Equipment status determines online topology. Transformer outages are branch outages; there is no separate transformer table. Unknown Pmax is explicitly reported as unknown by GridGuard. VoltVAR device lists bind controls by bus/branch ID.
