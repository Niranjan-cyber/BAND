# frontend/

Put your practiced frontend kit here (framework + component library) and copy `../frontend/src/styles/tokens.css`
usage into it. Required properties:
- Reads the API base URL from a build-time env var set by the pipeline (never typed by hand).
- Every screen root carries `data-mode="live|sample|fixture"`; sample/fixture screens show a visible badge.
- Ready components for loading, empty, error and rejected/blocked states.
- A health/version indicator that shows which API it is talking to (helps catch wrong-API bugs).
