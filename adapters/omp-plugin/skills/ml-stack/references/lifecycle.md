# Lifecycle contract

The canonical phase order is discovery → requirements lock → data audit → research → model/compute choice → training or experiment → evaluation → promotion → independent audit. Each phase records owner, inputs, outputs, approvals, unknowns, and exact artifact paths. A phase may abstain; it must not silently skip a gate. `ml-stack` coordinates, while sibling skills own phase details.

A handoff contains: objective, locked requirements revision, input revisions and hashes, decision or result, provenance, risks, approval state, and next owner. A result without those fields is not promotion-ready.
