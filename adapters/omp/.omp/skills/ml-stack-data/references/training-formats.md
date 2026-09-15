# Training formats

SFT requires ordered messages or prompt/completion with role and loss-mask semantics. DPO requires prompt, chosen, rejected, and consistent tokenizer policy. GRPO requires prompts plus a reward contract and generation constraints. Vision tasks require task-specific labels and coordinate conventions. Formatter output is versioned, deterministic, count-checked, and handed to `ml-stack-training`.
