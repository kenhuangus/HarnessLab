# HarnessLab Locked Contracts

HarnessLab is the companion GitHub project for *Hill Climbing: Design Patterns for Securing Long-Horizon Multi-Agent AI Systems*. The repository is intentionally runnable without cloud credentials or paid model APIs so instructors can use it in classrooms, workshops, and CI environments.

These contracts are locked for chapter implementations:

1. Every chapter must be executable through `python -m chapters.chXX.run` and through `harnesslab run chXX`.
2. Every chapter runner must return a `harnesslab.core.LabResult` with deterministic `passed`, `score`, `summary`, `decisions`, and `artifacts` fields.
3. Chapter code may use only the Python standard library unless the dependency is added to `pyproject.toml` and covered by tests.
4. Chapter code must model a realistic production harness control, not a prompt-only demonstration.
5. The core framework owns shared abstractions: identity, intent, autonomy, context, memory, observability, runtime steering, scalability, and governance.
6. Chapter folders own only chapter-specific adapters, scenarios, fixtures, README files, and captured `LabResult/` outputs.
7. No chapter may require live network access, real secrets, paid model APIs, or a particular vendor account.
8. Tests must verify both the success path and at least one blocked or escalated unsafe path for each chapter.
9. Long-running-agent considerations must appear in every chapter README and in the executable behavior where relevant.
10. The top-level README and each chapter README must be teaching documents, not thin launch notes.
11. Every chapter must include a `LabResult/` folder with `result.json`, `stdout.txt`, `stderr.txt`, and `README.md` captured from the public CLI.

The public CLI contract is:

```bash
python -m harnesslab.cli list
python -m harnesslab.cli run ch01
python -m harnesslab.cli run all
python scripts/capture_lab_results.py ch07
harnesslab run ch07 --json
```

The public Python contract is:

```python
from harnesslab.labs import run_lab

result = run_lab("ch07")
assert result.passed
print(result.to_json())
```
