---
name: python-tests
description: Apply this skill whenever writing or modifying Python tests. Use when the project is a Python codebase and test authoring is happening — creating test files, adding test functions, working with pytest, parametrize, fixtures, or test_*.py files. Also trigger when the user mentions pytest, conftest, or Python test structure, or when editing any file matching test_*.py or *_test.py.
user-invocable: false
---

# Python Test Conventions

- Flat pytest functions, no test classes.
- Merge near-identical tests into a single parametrized test. Label cases with `pytest.param(..., id="")`.
- Test file mirrors source file: tests for `module/file.py` live in `module/test_file.py` unless it is an integration test spanning multiple components.
