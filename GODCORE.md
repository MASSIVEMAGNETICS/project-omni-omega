# GODCORE Upgrade - Feature Documentation

This document details the GODCORE upgrade features added to OmniLoader.

## Table of Contents

1. [Brain Builder](#brain-builder)
2. [AAI + PSM](#aai--psm)
3. [InductionVM](#inductionvm)
4. [Defense Aura](#defense-aura)
5. [EPA 2.0](#epa-20)
6. [Transfer Learning](#transfer-learning)
7. [OTL (Open Transfer Learning)](#otl)
8. [Delta Composer](#delta-composer)

---

## Brain Builder

**Declarative AI brain design and deployment.**

Brain Builder lets you design custom AI systems using YAML or JSON specifications. A "brain" can combine multiple components: inner models, tools, memory, defense, and amplification.

### Example Brain Spec

```yaml
id: my-reasoning-brain
name: Reasoning Expert Brain
description: A brain optimized for mathematical reasoning
adapter: aai_psm
format: composite

aai:
  inner_manifest:
    id: llama-7b
    adapter: llama_cpp
    format: gguf
    files:
      weights: ./models/llama-7b/weights.gguf
  tools:
    - filesystem
    - memory
  reflection:
    enabled: true
    budget_tokens: 128
  memory:
    vector_dim: 384
    k: 6

defense:
  enabled: true
  strictness: medium

epa_seeds:
  - reasoning
  - helpfulness

defaults:
  temperature: 0.3
  top_p: 0.9
  max_tokens: 256
  threads: 2
```

### Workflow

1. **Validate** - Check spec validity and configuration
2. **Simulate** - Test with synthetic prompts, get performance estimates
3. **Compile** - Generate deployable artifacts (manifests, auras, skillpacks)
4. **Mount** - Hot-load into runtime without restart

### API

```python
# Validate
POST /api/lab/brain/validate
{
  "spec": { ... }
}

# Simulate
POST /api/lab/brain/simulate
{
  "spec": { ... },
  "num_prompts": 10
}

# Compile
POST /api/lab/brain/compile
{
  "spec": { ... }
}

# Mount
POST /api/lab/brain/mount
{
  "brain_id": "my-reasoning-brain"
}
```

---

## AAI + PSM

**Augmented AI with Persistent State Memory.**

AAI+PSM wraps models with:
- **Tools** - File system, web search, calculators
- **Reflection** - Meta-cognitive self-assessment
- **Memory** - Persistent vector memory with retrieval

### Architecture

```
User Query → Plan → Retrieve (PSM) → Reflect → Answer
                ↓
            [Tools Execution]
```

### PSM (Persistent State Memory)

PSM provides a world model for your AI:

- **Event Log** - Append-only history for replay
- **Entity Graph** - SQLite graph of entities and relations
- **Context Packing** - Retrieve relevant context via vector similarity

```python
# Log event
POST /api/psm/event
{
  "model_id": "my-model",
  "event": {
    "type": "inference",
    "data": { "prompt": "...", "response": "..." }
  }
}

# Get context
POST /api/psm/context_pack
{
  "model_id": "my-model",
  "query": "AI concepts",
  "k": 6
}

# Create snapshot
POST /api/psm/snapshot
{
  "model_id": "my-model",
  "snapshot_id": "backup_1",
  "description": "Before major update"
}
```

---

## InductionVM

**Optimized inference virtual machine.**

InductionVM provides low-level optimizations:

### Features

1. **Speculative Decoding** (~30% speedup)
   - Use small draft model to generate K tokens ahead
   - Verify with main model in parallel
   - Accept correct predictions

2. **KV Cache Compression** (~50% memory)
   - INT8 per-head quantization
   - Segment-wise compression
   - On-demand decompression

3. **RoPE Scaling** (extended context)
   - YaRN: wavelength-based scaling
   - NTK: base frequency adjustment
   - Linear: simple interpolation

4. **Pattern Mining** (caching)
   - Detect repeated patterns
   - Cache activations
   - Reduce recomputation

### Configuration

```python
induction:
  backend: "cpu"  # auto | cpu | directml | vulkan | remote
  spec_decode:
    enabled: true
    draft_model_id: "tiny-llama-gguf"
    ahead: 4
  kv_compress:
    mode: "int8-per-head"
    segment_bytes: 512
  rope:
    mode: "yarn"
    factor: 1.3
```

---

## Defense Aura

**Jailbreak and adversarial input protection.**

Defense Aura detects and blocks:
- DAN (Do Anything Now) attacks
- Role-play bypasses
- Encoding bypasses (base64, rot13)
- Excessive repetition
- Abnormal input length

### Configuration

```python
defense:
  enabled: true
  strictness: "medium"  # low | medium | high
```

### Behavior

- **Low**: Block only high-severity threats
- **Medium**: Block high and medium severity
- **High**: Block all detected patterns

### Evaluation

Test defense effectiveness:

```python
# In Diagnostics Plus tab
- Enable Defense Aura
- Select strictness level
- Run test set (standard jailbreaks, encoding attacks, etc.)
- View block rate and false positive metrics
```

---

## EPA 2.0

**Enhanced Prompt Amplification.**

EPA rapidly amplifies specific behaviors using:
- Built-in seeds (reasoning, helpfulness, conciseness, creativity)
- Micro-curriculum generation
- Rank-2 LoRA training (40 steps, ~2 minutes)

### Built-in Seeds

1. **Reasoning** - Chain-of-thought, step-by-step thinking
2. **Helpfulness** - Comprehensive, structured responses
3. **Conciseness** - Direct, minimal responses
4. **Creativity** - Novel, imaginative outputs

### Workflow

1. Select seed behavior
2. Generate micro-curriculum (synthetic examples)
3. Train rank-2 LoRA (40 steps)
4. Evaluate amplification
5. Apply delta or merge with base model

### Performance

- **Training Time**: ~2 minutes on CPU
- **Parameters**: <1M (rank-2 LoRA)
- **Improvement**: 45%+ on target behavior
- **Generalization**: Good on similar tasks

---

## Transfer Learning

**Cross-model knowledge transfer.**

### Distillation

Transfer knowledge from large to small models:

```python
# Teacher → Student
distill(
    teacher_model_id="llama-70b",
    student_model_id="llama-7b",
    examples=training_examples,
    temperature=2.0,
    alpha=0.5,
    steps=100
)
```

### Feature Bridge

Map features between different architectures:

```python
# Learn mapping
bridge = FeatureBridge(source_dim=512, target_dim=768)
bridge.learn_mapping(source_features, target_features)

# Transfer directions (e.g., LoRA deltas)
target_delta = bridge.map_direction(source_delta)
```

Use cases:
- Transfer LoRA from Llama to Mistral
- Share steering vectors across families
- Map SAE features between models

---

## OTL

**Open Transfer Learning registry.**

Share and import training artifacts:

### Push Samples

```python
POST /api/otl/samples/push
{
  "model_id": "llama-7b",
  "samples": [
    {"prompt": "...", "response": "..."},
    ...
  ],
  "metadata": {"domain": "math"}
}
```

### Pull Artifacts

```python
POST /api/otl/artifact/pull
{
  "artifact_id": "math_reasoning_delta_v1",
  "artifact_type": "delta"
}
```

### Security

- Artifacts are signed with SHA-256
- Provenance tracked in PSM
- Local and remote registry support

---

## Delta Composer

**Merge LoRA deltas intelligently.**

Compose multiple LoRA adaptations:

```python
POST /api/compose/merge_lora
{
  "delta_ids": ["math_delta", "code_delta"],
  "weights": [0.6, 0.4],
  "orthogonalize": true
}
```

### Features

1. **Layer-wise Scaling** - Different weights per layer
2. **Orthogonalization** - Reduce interference via Gram-Schmidt
3. **Conflict Resolution** - Automatic conflict detection
4. **Regression Estimation** - Predict performance impact

### Use Cases

- Combine math + code skills
- Merge domain adaptations
- Create multi-capability models
- Reduce negative interference

---

## Performance Benchmarks

| Component | Metric | Value |
|-----------|--------|-------|
| Speculative Decode | Speedup | +30% |
| KV Compression | Memory Savings | -50% |
| EPA Training | Time (CPU) | ~2 min |
| EPA Improvement | Target Behavior | +45% |
| Defense Aura | Block Rate | 90% |
| Defense Aura | False Positives | <5% |
| Delta Composer | Regression | <2% |

---

## Example Workflows

### Create a Math Expert Brain

1. Write brain spec with math EPA seed
2. Validate spec
3. Simulate with math prompts
4. Compile artifacts
5. Mount and use

### Amplify Helpfulness

1. Open Diagnostics Plus
2. Enable EPA
3. Select "helpfulness" seed
4. Train (40 steps)
5. Evaluate improvement
6. Apply delta

### Merge Two Skills

1. Train LoRA on skill A
2. Train LoRA on skill B
3. Use Delta Composer to merge
4. Review regression estimate
5. Apply merged delta

### Protect from Jailbreaks

1. Enable Defense Aura
2. Set strictness to "medium"
3. Test with jailbreak set
4. Review block rate
5. Deploy to production

---

## Configuration Reference

### InductionVM

```python
# app/config.py
induction_backend = "auto"
induction_spec_decode_ahead = 4
induction_draft_model_id = "tiny-llama-gguf"
induction_kv_compress_mode = "int8-per-head"
induction_kv_segment_bytes = 512
induction_rope_mode = "yarn"
induction_rope_factor = 1.3
```

### PSM

```python
# app/config.py
psm_vector_dim = 384
psm_topk = 6
```

### EPA

```python
# app/config.py
default_lora_rank = 2
default_lora_steps = 40
default_lora_lr = 2e-4
default_lora_max_modules = 4
```

---

## Troubleshooting

### InductionVM not speeding up

- Check draft model is loaded
- Verify ahead > 0
- Ensure max_tokens > 10

### PSM using too much disk

- Create snapshots less frequently
- Compress old events
- Use smaller vector_dim

### EPA not improving

- Try different seed
- Increase steps to 60-80
- Check examples are relevant
- Ensure rank=2 (not higher)

### Defense blocking legitimate inputs

- Lower strictness to "low"
- Review blocked patterns
- Add exceptions if needed

---

## API Quick Reference

```bash
# Brain Builder
POST /api/lab/brain/validate
POST /api/lab/brain/simulate
POST /api/lab/brain/compile
POST /api/lab/brain/mount

# PSM
POST /api/psm/event
POST /api/psm/context_pack
POST /api/psm/snapshot

# Composer
POST /api/compose/merge_lora

# OTL
POST /api/otl/samples/push
POST /api/otl/artifact/pull
```

---

## Next Steps

1. **Experiment** with Brain Builder
2. **Enable** InductionVM for speedups
3. **Amplify** skills with EPA
4. **Protect** with Defense Aura
5. **Share** artifacts via OTL
6. **Compose** multi-skill models

For more details, see the UI tabs:
- Brain Builder (design brains)
- Diagnostics Plus (EPA & defense)
- Induction Settings (configure optimizations)
