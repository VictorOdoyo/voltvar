# Validation record

Local validation: Python 3.13.15, NumPy 2.1.2, Windows, 2026-10-24. 231 tests pass, including 200 closed-form, inverse-construction or fresh-solve reference cases. Case files and derivations live in references/ and docs/references/. Independent oracle values are not harvested from the implementation under test. Each complete case is committed with its fixture, test and derivation together.

The external case9 reference comes from the public MATPOWER nine-bus case solved independently by PYPOWER 5.1.21. Original source URL and upstream data/license notes are retained in benchmarks/. Bus voltage tolerance 1e-8 pu, angle tolerance 1e-6 degrees, branch power tolerance 2e-6 MW/MVAr across Newton, Gauss–Seidel and fast-decoupled methods.

CI installs the package and runs all tests on Python 3.11/3.12/3.13. The installed CLI is exercised from outside the repository. Workbench previews are captured from real local results. Documentation states approximation limits; no external field-compliance certificate is implied.
