---
name: python-type-annotations-and-regression-tests
description: Use when writing or fixing Python code packages that require strict type checking, dedicated regression test files, and changelog updates.
---
- Do not modify existing test files in the original test suite; add new tests in a separate, dedicated test file.
- Add complete type annotations (parameters and return values) to every public function where the function name does not start with an underscore.
- Create a dedicated regression test file with at least one test function per bug fixed (minimum required test functions).
- Record every bug fix as a bullet point under the unreleased heading in the changelog file using the format `- fix(<function name>): <short description>`.