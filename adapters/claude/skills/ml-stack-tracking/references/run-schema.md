# Run and event schema

A run has stable ID, project, parent, status, actor, timestamps, immutable config/input revisions, environment, resource profile, and privacy class. Events have sequence, timestamp, run ID, type, payload, source, and content hash. Config, metric, artifact, heartbeat, error, and state events are replayable JSON.
