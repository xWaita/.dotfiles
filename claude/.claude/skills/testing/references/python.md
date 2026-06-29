# Python Test Conventions

- Flat pytest functions, no test classes.
- Merge near-identical tests into a single parametrized test. Label cases with `pytest.param(..., id="")`.
- Test file mirrors source file: tests for `module/file.py` live in `module/test_file.py` unless it is an integration test spanning multiple components.
