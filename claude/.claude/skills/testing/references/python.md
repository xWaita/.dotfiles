# Python Test Conventions

> Self-describing: fold future learnings into this file directly — never into Claude memory (memory does not transfer between machines). Keep it generic, concise, well-structured.

- Flat pytest functions, no test classes.
- Merge near-identical tests into a single parametrized test. Label cases with `pytest.param(..., id="")`.
- Test file mirrors source file: tests for `module/file.py` live in `module/test_file.py` unless it is an integration test spanning multiple components.
- Mock an external service at the request level with its client's mocking library — respx for httpx, moto for boto3 — never by patching the code under test or swapping its client.
