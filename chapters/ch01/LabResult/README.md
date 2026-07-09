# **LabResult for CH01**

This folder stores the captured run result for `ch01`.

Generated command:

```bash
python -m harnesslab.cli run ch01 --json
```

Files:

- `result.json`: parsed `LabResult` object returned by the public HarnessLab CLI.
- `stdout.txt`: raw standard output from the CLI run.
- `stderr.txt`: raw standard error from the CLI run. This should normally be empty.

The repository QA gate validates that this result is present, parseable, chapter-matched, passing, and supported by decisions and artifacts.
