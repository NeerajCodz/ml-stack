# Resume and orphan recovery

Use stable run and checkpoint IDs, heartbeat timestamps, owner, provider job ID, last event, and artifact location. Detect lost heartbeats and orphaned resources before retry. Resume only from verified compatible state; cancellation and cleanup require approval unless an expiry policy explicitly covers the resource.
