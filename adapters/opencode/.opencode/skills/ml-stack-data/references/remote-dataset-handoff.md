# Remote dataset inspection handoff

When the runtime lacks Dataset Viewer or remote HF operations, emit dataset URL/ID, exact revision, intended split and fields, bounded sample/statistics queries, privacy redaction rules, expected response schema, and operator approval. Mark all values unknown until observed. Hand off the resulting contract to `ml-stack-training` or `ml-stack-audit`.
