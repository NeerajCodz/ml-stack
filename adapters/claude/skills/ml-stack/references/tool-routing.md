# Callable tool routing

The registry currently exposes exactly these seven operations:

- `ml_stack.status`: inspect runtime and ledger status.
- `ml_stack.init`: initialize project state after approval.
- `ml_stack.discover`: inventory a project path.
- `ml_stack.audit_data`: inspect supported local dataset metadata and samples.
- `ml_stack.capture_requirements`: compile and lock explicit requirements.
- `ml_stack.research`: run bounded paper-first retrieval with citations.
- `ml_stack.events`: replay append-only ledger events.

No tool name for training, jobs, benchmarks, tracking providers, deployment, Hub writes, or publication may be presented as executable. For those phases produce a bounded plan/handoff with inputs, commands or API intent, approval gate, expected outputs, and abstention conditions.
