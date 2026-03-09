# GEMINI.md — NeuralOS: Complete Architecture, Current State & Final Build Specification

**Version:** 0.1.0 (Synapse) → target 1.0.0 (Cortex)  
**Base:** Arch Linux (`archlinux:base-devel`)  
**Deliverable:** Docker container today; bare-metal ISO for 1.0.0  
**Hardware target:** Mid-range (8 GB RAM, integrated GPU, x86_64 or ARM64)  
**Philosophy:** AI is the OS. Not bolted on. Not an assistant. The kernel decisions, memory management, file indexing, anomaly detection, scheduling, and package management are all driven by trained neural models that improve continuously during normal use.

---

## Table of Contents

1. [What NeuralOS Is](#1-what-neurlos-is)
2. [Current State — v0.1.0 Exact Inventory](#2-current-state--v010-exact-inventory)
3. [Full Repository Layout](#3-full-repository-layout)
4. [Architecture: How All Layers Connect](#4-architecture-how-all-layers-connect)
5. [Every Existing Module — Deep Reference](#5-every-existing-module--deep-reference)
6. [OS-Layer Binaries & Configuration](#6-os-layer-binaries--configuration)
7. [Build & Container System](#7-build--container-system)
8. [Planned Features: Scoped & Designed](#8-planned-features-scoped--designed)
9. [Final Build Target: v1.0.0 Cortex](#9-final-build-target-v100-cortex)
10. [Extension Recipes](#10-extension-recipes)
11. [Runtime State & Log Files](#11-runtime-state--log-files)
12. [Configuration Reference](#12-configuration-reference-etcnosnos.conf)
13. [Testing](#13-testing)
14. [Known Constraints & Intentional Decisions](#14-known-constraints--intentional-decisions)
15. [Quick API Reference for AI Agents](#15-quick-api-reference-for-ai-agents)

---

## 1. What NeuralOS Is

NeuralOS is an Arch Linux–based operating system built around the principle that every traditional OS heuristic — round-robin scheduling, LRU page eviction, name-based file lookup, static dependency resolution — should be replaced by a trained model that learns from the machine it runs on.

The user experience is a hybrid: boots to a rich TUI shell (`nos-shell`) with a keyboard-driven AI interface. An optional GUI layer (`PicoClaw`, planned) sits on top. The AI subsystems run as background systemd services, continuously observing and learning. A federated learning protocol lets a fleet of NeuralOS nodes share model improvements without sharing raw data.

It is not Ubuntu with ChatGPT glued on. It is a purpose-built Linux distro where the intelligence lives in `/usr/lib/nos/` and every OS decision routes through `NeuralNode`.

---

## 2. Current State — v0.1.0 Exact Inventory

### What is built and working

| Component | File | Status | Tests |
|---|---|---|---|
| Neural kernel primitives | `kernel/nn_core.py` | ✅ Complete | ✅ |
| Semantic filesystem | `services/ai_services.py` | ✅ Complete | ✅ |
| Anomaly detector | `services/ai_services.py` | ✅ Complete | ✅ |
| Resource predictor | `services/ai_services.py` | ✅ Complete | ✅ |
| Context engine | `services/ai_services.py` | ✅ Complete | ✅ |
| Neural memory compressor | `compressor/neural_compressor.py` | ✅ Complete | ✅ |
| Predictive file cache | `cache/predictive_cache.py` | ✅ Complete | ✅ |
| Conversational diagnostics | `diagnostics/conversational_diagnostics.py` | ✅ Complete | ✅ |
| AI package manager | `pkg_manager/neural_pkg_manager.py` | ✅ Complete | ✅ |
| NeuralNode integration | `system.py` | ✅ Complete | ✅ |
| nos-init (PID 1 shim) | `usr/bin/nos-init` | ✅ Complete | manual |
| nos-shell (login shell) | `usr/bin/nos-shell` | ✅ Complete | manual |
| nos CLI tool | `usr/bin/nos` | ✅ Complete | manual |
| nos-login | `usr/bin/nos-login` | ✅ Complete | manual |
| nos-sysinfo | `usr/bin/nos-sysinfo` | ✅ Complete | manual |
| Dockerfile (multi-stage) | `Dockerfile` | ✅ Complete | ✅ |
| docker-compose.yml | `docker-compose.yml` | ✅ Complete | — |
| systemd service units | `usr/lib/systemd/system/` | ✅ Complete | — |
| OS identity & config | `/etc/nos/` | ✅ Complete | — |
| Test suite | `test_all.py` | ✅ 83/83 passing | — |

### What is not yet built (planned in this spec)

- PicoClaw GUI window manager
- NOS Agent (agentic AI shell with tool use)
- Real kernel module (`nos.ko`)
- Live federated gradient sync over network
- Model weight persistence to disk
- pacman integration in package manager
- PAM behavioural authentication module
- `/proc/nos/` virtual filesystem
- Rolling update system with PoL verification
- AI-driven process sandboxing

---

## 3. Full Repository Layout

```
NeuralOS-distro/
│
├── Dockerfile                        Multi-stage: nos-base → nos-runtime → nos-full
├── docker-compose.yml                Primary node + optional federated peer
├── build.sh                          build | run | nsh | test | clean | status | logs
├── README.md                         User-facing documentation
├── GEMINI.md                         This file
│
└── rootfs/                           Mirrors container filesystem exactly
    │
    ├── etc/
    │   ├── nos/
    │   │   ├── nos.conf              Master config (all AI tuning knobs)
    │   │   └── os-release            OS identity
    │   ├── profile.d/
    │   │   └── nos.sh                Login environment: PYTHONPATH, aliases, PS1
    │   └── skel/
    │       └── .nosrc                Default user RC (sourced by nos-shell)
    │
    ├── usr/
    │   ├── bin/
    │   │   ├── nos                   Main CLI tool
    │   │   ├── nos-init              PID 1 / boot / service orchestrator
    │   │   ├── nos-shell             AI-aware login shell
    │   │   ├── nos-login             Login program (auto-login in container)
    │   │   └── nos-sysinfo           Neofetch-style system display
    │   │
    │   └── lib/
    │       ├── nos/                  PYTHONPATH root — all AI modules live here
    │       │   ├── __init__.py
    │       │   ├── system.py         NeuralNode master class + NeuralOSNetwork
    │       │   ├── neural_shell.py   Rich TUI (alternative to nos-shell)
    │       │   ├── test_all.py       83-test suite
    │       │   │
    │       │   ├── kernel/
    │       │   │   └── nn_core.py    DenseLayer, MLP, Autoencoder, EmbeddingLayer,
    │       │   │                     AttentionLayer, ModelCompressor
    │       │   ├── services/
    │       │   │   └── ai_services.py  SemanticFileSystem, AnomalyDetector,
    │       │   │                       ResourcePredictor, ContextEngine
    │       │   ├── compressor/
    │       │   │   └── neural_compressor.py  DeltaEncoder, NeuralPatternPredictor,
    │       │   │                              TieredMemoryManager
    │       │   ├── cache/
    │       │   │   └── predictive_cache.py  MarkovAccessPredictor, TimePatternModel,
    │       │   │                             LRUKEviction, PredictiveCache
    │       │   ├── diagnostics/
    │       │   │   └── conversational_diagnostics.py  Issue, ISSUE_KB, SymptomMatcher,
    │       │   │                                        AutoHealer, ConversationalDiagnostics
    │       │   └── pkg_manager/
    │       │       └── neural_pkg_manager.py  Package, DEFAULT_PACKAGES,
    │       │                                   DependencyResolver, PackageHealthScorer,
    │       │                                   InstallPatternLearner, NeuralPkgManager
    │       │
    │       └── systemd/system/
    │           ├── nos-anomaly.service
    │           ├── nos-resource-monitor.service
    │           ├── nos-trainer.service
    │           └── nos.target
    │
    └── var/
        ├── lib/nos/                  state.json, packages.json, models/ (future)
        ├── log/nos/                  init.log, anomaly.log, resources.log, shell.log
        └── cache/nos/                Cache storage
```

---

## 4. Architecture: How All Layers Connect

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        USER INTERFACE LAYER                             ║
║                                                                          ║
║   nos-shell (login shell)     nos CLI (/usr/bin/nos)                    ║
║   PicoClaw WM [planned]       NOS Agent [planned]                       ║
╠══════════╦═══════════╦══════════════╦═══════════════╦════════════════════╣
║ Semantic ║ Predictive║ Conversational║  AI Package   ║  NOS Agent        ║
║   File   ║   Cache   ║  Diagnostics  ║   Manager     ║  [planned]        ║
║  System  ║ (Markov + ║ (SymptomMatch ║ (collab filter║  Tool executor    ║
║(hash-emb)║ time-day) ║ + AutoHealer) ║ + dep resolve)║  Plan + act loop  ║
╠══════════╩═══════════╩══════════════╩═══════════════╩════════════════════╣
║                    NeuralNode  (nos/system.py)                           ║
║       run_command() · dashboard() · simulate_activity()                  ║
║       spawn_process() · kill_process() · event_log()                    ║
╠══════════╦═══════════╦══════════════╦═══════════════╦════════════════════╣
║ Anomaly  ║ Resource  ║    Neural    ║    Context    ║  Federated        ║
║ Detector ║ Predictor ║  Compressor  ║    Engine     ║  Learning         ║
║(autoenc. ║(MLP window║(delta+zlib   ║(detects mode: ║  [stub → real]    ║
║ 3-sigma) ║ forecast) ║ 3-tier RAM)  ║coding/ops/...) ║  DP gradients     ║
╠══════════╩═══════════╩══════════════╩═══════════════╩════════════════════╣
║                 Neural Kernel  (nos/kernel/nn_core.py)                   ║
║   DenseLayer · MLP · Autoencoder · EmbeddingLayer · AttentionLayer      ║
║   ModelCompressor (8-bit quantise + zlib, 4-8x ratio)                   ║
╠══════════════════════════════════════════════════════════════════════════╣
║              nos-init (PID 1) · ServiceDaemon threads · systemd units    ║
╠══════════════════════════════════════════════════════════════════════════╣
║         Arch Linux  (pacman · systemd · glibc · Linux kernel)            ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Data flow: user types a command

```
nos-shell input
    │
    ▼
shlex.split() → cmd token
    │
    ├─ BUILTINS dict match → cmd_*() function → direct subsystem call
    │
    ├─ DIAG_KEYWORDS set match → NeuralNode.run_command() → ConversationalDiagnostics
    │
    ├─ NeuralNode.run_command() pattern match:
    │     "find *"          → SemanticFileSystem.semantic_search()
    │     "install *"       → NeuralPkgManager.install()
    │     "remove *"        → NeuralPkgManager.remove()
    │     "diagnose/fix/..."→ ConversationalDiagnostics.chat()
    │     "memory/compress" → TieredMemoryManager.memory_report()
    │     "cache"           → PredictiveCache.cache_report()
    │     "predict/forecast"→ ResourcePredictor.predict()
    │     "status/dashboard"→ NeuralNode.dashboard()
    │     "spawn *"         → NeuralNode.spawn_process()
    │
    └─ subprocess.run(shell=True) fallback → /bin/bash

Result dict always has 'type' key.
nos-shell._render_result() switches on 'type' for ANSI rendering.
```

### Background service data flow (running always)

```
ServiceDaemon threads (started by nos-init):

  nos-anomaly      [every 10s]  → psutil → AnomalyDetector.observe()
                                          → /var/log/nos/anomaly.log

  nos-resource     [every 5s]   → psutil → /var/log/nos/resources.log
  -monitor

  nos-cache        [every 30s]  → TimePatternModel.record()
  -warmer                         PredictiveCache.put() pre-warm

  nos-trainer      [once/boot]  → NeuralNode.simulate_activity(n_ticks=20)
                                  warms all MLP models with synthetic data
```

---

## 5. Every Existing Module — Deep Reference

### 5.1 `nos/kernel/nn_core.py` (379 lines)

The entire neural network foundation. Pure NumPy. No PyTorch, no TensorFlow.

#### Activation functions
`relu`, `relu_grad`, `sigmoid`, `sigmoid_grad`, `tanh_act`, `tanh_grad`,
`softmax`, `leaky_relu` (α=0.01), `gelu` (tanh approximation).
`ACTIVATIONS` dict: name → (forward_fn, grad_fn).

#### `DenseLayer`
Fully-connected layer. He init for relu/leaky_relu/gelu; Xavier for sigmoid/tanh.
Adam optimizer state (mW, vW, mb, vb, t) stored per-layer.
Dropout applied at training time only (inverted scaling: `a / (1 - rate)`).
`forward()` caches x, z, a. `backward()` returns (grad_x, grad_W, grad_b).
`update_adam()` applies L2 weight decay + Adam update.
`get_params()` / `set_params()` for serialisation.
`param_count()` → total parameter count for this layer.

#### `EmbeddingLayer`
Matrix E: shape (vocab_size, embed_dim). Random init ×0.1.
`forward(indices)` → row lookup. `backward(grad, lr)` → scatter-add update.
`cosine_similarity(a, b)` → float. `nearest(query, top_k)` → sorted indices by cosine.

#### `AttentionLayer`
Q/K/V/O weight matrices init ×0.1. Single-pass `forward(x, mask)`.
Scale = √(head_dim). Softmax on scores. Optional causal mask.
Forward-only; no backprop implemented yet.

#### `MLP`
Stacks N `DenseLayer` instances. `activations` defaults to `['relu']*(N-1) + ['linear']`.
`train_step(x, y, task)` → one forward+backward+Adam step, returns scalar loss.
`predict(x)` → sets training=False, forward pass, restores training=True.
`get_all_params()` / `set_all_params()` for model serialisation.
Loss: `mse_loss` (regression) or `cross_entropy_loss` (classification, uses softmax internally).

#### `ModelCompressor`
Static methods. `quantize_weights(W, bits=8)` → (bytes, w_min, scale).
`dequantize_weights(data, shape, w_min, scale)` → float32.
`prune_weights(W, sparsity=0.3)` → zeroes smallest-magnitude weights.
`compress_model(mlp)` → quantise all layers, join with `|` separator, zlib level 9.
`compressed_size_kb(mlp)` / `float32_size_kb(mlp)` for comparison.
Typical compression: 4–8× ratio with <1% accuracy loss.

#### `Autoencoder`
Encoder: `MLP([input_dim, hidden, bottleneck], ['relu', 'tanh'])`.
Decoder: `MLP([bottleneck, hidden, input_dim], ['relu', 'linear'])`.
`hidden = max(input_dim // 2, bottleneck * 2)`.
`reconstruction_error(x)` → per-sample MSE array (used as anomaly score).
`train_step(x)` → encode → decode → backprop through both, returns scalar loss.

---

### 5.2 `nos/services/ai_services.py` (419 lines)

#### `_hash_embed(text, dim=64)` — module function
Deterministic pseudo-embedding. Tokenises with `\w+`. For each token: MD5 → 128-bit int,
iterates dim bits, adds +1 or -1 per dimension. L2-normalises result.
Deterministic, zero-training, <1ms. Not geometrically semantic but sufficient for cosine ranking.

#### `FileRecord` (dataclass)
path, content_hash (16-hex SHA-256), embedding (float32[64]), tags (List[str]),
size_bytes, last_modified, access_count, last_accessed.

#### `SemanticFileSystem`
`_index`: dict path→FileRecord. `_tag_index`: dict tag→[paths]. `_access_log`: list (ts, path).

`index_file(path, content_hint, tags, size_bytes)`:
text = `basename + hint + tags`. Calls `_hash_embed`. SHA-256 first 16 chars.
Calls `_auto_tag` if tags not provided. Stores in both indexes.

`_auto_tag(path, hint)`:
Extension map: .py→['code','python'], .pdf→['document','pdf'], .csv→['data','spreadsheet'],
.json→['data','config'], .log→['log','system'], .sh→['script','shell'], etc.
Keyword scan of combined path+hint: 'tax'→'finance', 'config'→'config', 'readme'→'documentation'.

`semantic_search(query, top_k, tag_filter)`:
Embeds query. Cosine against all candidates. Adds `_recency_boost`:
`0.05 × max(0, 1 - age_days/30)`. Returns sorted (score, FileRecord) top_k.

`record_access(path)`: increments access_count, updates last_accessed, appends to access_log.
`hot_files(top_k)`: sorted by access_count descending.
`stats()`: {indexed_files, unique_tags, total_size_mb}.

#### `AnomalyDetector`
Feature vector: 28 dims.
Syscall dims (20): normalised frequencies of read, write, open, close, mmap, fork, exec,
socket, connect, accept, bind, listen, mprotect, brk, ioctl, select, poll, epoll, stat, dup.
Metric dims (8): cpu_pct/100, mem_pct/100, net_bytes/1e7, disk_ops/1000,
open_fds/1024, thread_count/200, ctx_switches/1e4, uptime_s/86400.
Model: `Autoencoder(28, bottleneck=4)` → architecture 28→14→4→14→28.
Error history: deque(maxlen=200). Trains every 10 observations. Threshold = μ + 3σ.
Severities: calibrating < normal < elevated (0.5×) < warning (1.0×) < critical (2.0×).

#### `ResourcePredictor`
CPU and memory MLP each: architecture `[30, 32, 16, 5]`, activations ['relu','relu','linear'], lr=5e-4.
Records normalised values (÷100) in deques. Trains via sliding-window on full history each call.
`predict()`: returns 5-step forecast for both CPU and RAM.
`spike_warning` = True if any forecast CPU>85 or RAM>90.
`recommend_action()`: non-None string when spike detected.

#### `ContextEngine`
Detects one of 9 modes: coding, browsing, media, writing, gaming, sysadmin, idle,
data_analysis, communication.
Mode hints (process keywords): coding=['python','node','gcc','vim','code','git','make'],
data_analysis=['jupyter','pandas','spark','R','matplotlib','sklearn'],
sysadmin=['systemctl','docker','kubectl','ansible','terraform','ssh'],
browsing=['firefox','chrome','chromium'],
media=['vlc','mpv','spotify','ffmpeg'], etc.
EMA blending α=0.2 on mode scores. `current_mode` = top scoring mode.
`suggested_prefetch_tags()`: maps mode → list of semantic tag categories for cache warm.

---

### 5.3 `nos/compressor/neural_compressor.py` (362 lines)

#### `MemoryRegion` (dataclass)
pid, region_id, base_address, size_bytes, data, is_compressed, compressed_data,
compression_ratio, last_accessed, access_count, dirty, region_type.

#### `CompressionStats` (dataclass)
original_bytes, compressed_bytes, regions_compressed/decompressed, compress/decompress_time_ms,
delta_hits, neural_assists. Properties: `ratio`, `savings_mb`.

#### `DeltaEncoder`
**Critical invariant:** `_enc` (encoder baseline) and `_dec` (decoder baseline) are
separate dicts. Must be called N encode times then N decode times in the same order.
Never share the same dict between encoder and decoder side.

`encode(region_id, data)`:
If baseline exists + same length + <40% bytes changed → XOR delta, prefix `\x01`.
Else keyframe, prefix `\x00`. Always advances `_enc[id]` to new data.

`decode(region_id, encoded)`:
`\x00` → store as `_dec[id]`, return raw data.
`\x01` → XOR payload vs `_dec[id]`, advance `_dec[id]` to decoded result.

`forget(region_id)`: clears both `_enc` and `_dec` entries.

#### `NeuralPatternPredictor`
n-gram table: defaultdict(int) for all 4-grams in training data.
Codebook: dict pattern→2-byte code (top-512 most frequent patterns).
Rebuilt every 64 KB of training data via `_rebuild_codebook()`.
`encode_assist(data)`: substitutes known patterns with `\xFF\xFE` + uint16 code.
`decode_assist(data)`: reverses substitution. Improves effective zlib ratio 10–20%.

#### `TieredMemoryManager`
Three in-process dicts: `_hot` (raw bytes), `_warm` (compressed), `_cold` (compressed).
`_hot_limit_bytes` = 512 MB. `_warm_limit_bytes` = 1024 MB.
`_stats`: `CompressionStats` instance.

`store(pid, region_id, data, region_type)`:
Calls `_predictor.learn(data[:4096])` first for pattern learning.
Places in hot if under limit, else `_compress_to_warm`.

`access(pid, region_id)`:
Hot → return directly. Warm → `_decompress_warm` → `_maybe_promote_to_hot`.
Cold → `_decompress_cold`. Updates access_count and last_accessed.

`_compress_to_warm(key, region)`: delta-encode (if baseline exists) → zlib level 3.
`_compress_to_cold(key, region, data)`: pattern-assist → zlib level 9. Increments neural_assists.
`_maybe_promote_to_hot(key, data, region)`: if access_count>3 and hot under limit, promote.

`evict_lru(target_free_mb)`:
Sorts hot by last_accessed, compresses LRU entries to warm until free.
Then sorts warm by last_accessed, recompresses LRU to cold if needed.

---

### 5.4 `nos/cache/predictive_cache.py` (386 lines)

#### `CacheEntry` (dataclass)
path, data (may be compressed), compressed (bool), original_size, stored_size,
access_times (list, max 20), prefetch_score, tags.
Properties: `access_count`, `last_accessed`, `access_frequency` (accesses/hour over 24h window).

#### `MarkovAccessPredictor`
`_transitions`: defaultdict(Counter). State = tuple of last 2 accessed paths.
`record_access(path)`: appends to `_history` (deque(3)), records order-2 transition.
`predict_next(top_k)`: looks up (file_{t-2}, file_{t-1}) state → normalised probabilities.
Falls back to order-1 (just last file) if state not found.
`_prune()`: removes states with total count <2 when dict exceeds 2000 entries.

#### `TimePatternModel`
`_hourly`: 24-slot Counter dict. `_day_buckets`: 7-slot Counter dict.
`record(path, ts)`: increments both. `predict_for_hour(hour, top_k)` → sorted by count.
`predict_next_hour(top_k)` → hour+1 mod 24. `predict_now(top_k)` → current hour.

#### `LRUKEviction` (K=2)
`_access_history`: dict path→deque(maxlen=2).
`eviction_candidate(candidates)`: returns candidate with oldest 2nd-most-recent access.
Files with fewer than 2 accesses get kth_time=0.0 (evicted first).

#### `PredictiveCache`
`_cache`: dict path→CacheEntry. `_hits`, `_misses`, `_prefetch_hits`, `_evictions`.
Compression: zlib level 1 if >512 bytes AND saves >10%.

`get(path)`: updates Markov+time+LRU-K, checks `_prefetch_set`, triggers `_trigger_prefetch()`.
`put(path, data, tags, prefetch_score)`: compresses if beneficial, evicts if needed.
`_trigger_prefetch()`: merges Markov top-5 + time top-3 into `_prefetch_queue` heapq.
`prefetch_by_context(context_tags, file_index)`: queries SemanticFileSystem, queues score>0.3.
`warm_from_time_model(file_loader_fn)`: calls predict_next_hour, loads top 15 files.
`cache_report()`: {cached_files, cache_size_mb, max_size_mb, utilisation_pct,
hit_rate_pct, prefetch_hit_rate_pct, evictions, compression_savings_mb, prefetch_queue_depth}.

---

### 5.5 `nos/diagnostics/conversational_diagnostics.py` (557 lines)

#### `Severity` (Enum)
INFO, WARNING, ERROR, CRITICAL (used for sorting and colour in output).

#### `Issue` (dataclass)
id, title, severity, description, symptoms (List[str]), root_causes (List[str]),
fixes (List[str]), auto_fixable (bool), affected_component (str).

#### `ISSUE_KB` — all 7 current issues

| ID | Severity | Symptom match keys | Auto-fixable |
|---|---|---|---|
| HIGH_CPU | WARNING | `cpu > 85` | yes |
| MEMORY_PRESSURE | WARNING | `mem > 88`, `swap > 20` | yes |
| ZOMBIE_PROCESSES | ERROR | `zombies > 5` | yes |
| ANOMALY_DETECTED | CRITICAL | `anomaly_score > threshold`, `severity == critical` | no |
| LOW_CACHE_HIT | INFO | `cache_hit < 40` | yes |
| PAGE_FAULT_STORM | ERROR | `page_faults > 500` | yes |
| FEDERATED_STALE | INFO | `federated_rounds_stale` | yes |

Adding a new issue: append `Issue(...)` to `ISSUE_KB`. The matcher, explainer,
and healer pick it up automatically. No other changes needed.

#### `SystemSnapshot` (dataclass)
cpu_pct, mem_pct, disk_pct, swap_pct, load_avg, process_count, zombie_count,
open_fds, page_fault_rate, anomaly_score, anomaly_severity, cache_hit_rate,
compression_ratio, top_cpu_processes (List[str]), top_mem_processes (List[str]),
recent_errors (List[str]), federated_round (int), model_accuracy (float), ts (float).

#### `SymptomMatcher`
`match(snapshot)` → sorted [(Issue, score)] for score>0.
Scoring: matched_symptom_count × severity_weight (CRITICAL=3, ERROR=2, WARNING=1.5, INFO=1).
`_score_issue(issue, snap)`: evaluates each symptom key against snap fields.

#### `AutoHealer`
`apply_fix(issue, snapshot, compressor, cache)`:
- HIGH_CPU → logs scheduler retrain request
- MEMORY_PRESSURE → `compressor.evict_lru(256)`
- ZOMBIE_PROCESSES → logs SIGCHLD reap
- LOW_CACHE_HIT → logs cache clear trigger
- PAGE_FAULT_STORM → logs memory pressure relief
- FEDERATED_STALE → logs sync trigger
- Others → returns manual instruction string
`fix_history()` → last 20 fix records with timestamps.

#### `ConversationalDiagnostics`
FSM: idle → diagnosing → fix_confirm → walkthrough.
`update_snapshot(snap)`: stores latest SystemSnapshot.
`chat(user_input, compressor, cache)` → formatted response string.

Routing (evaluated in order):
1. GREETINGS set or idle state → `_cmd_diagnose()`
2. regex 'diagnos|scan|check|analyse' → `_cmd_diagnose()`
3. regex 'fix|heal|repair|resolve' → `_cmd_fix()`
4. regex 'explain|what|why|detail|N' → `_cmd_explain(N)`
5. regex 'history|log|past' → `_cmd_history()`
6. keyword 'cpu' → `_cmd_component('cpu')`
7. keyword 'mem|memory|ram' → `_cmd_component('memory')`
8. keyword 'cache' → `_cmd_component('cache')`
9. keyword 'anomal|threat' → `_cmd_component('anomaly')`
10. fix_confirm state + YES_WORDS → `_apply_current_fix()`
11. fallback → `_generic_response()`

---

### 5.6 `nos/pkg_manager/neural_pkg_manager.py` (462 lines)

#### `Package` (dataclass)
name, version, description, categories (List[str]), depends (List[str]),
conflicts (List[str]), size_kb, install_count, last_updated_days,
has_cve, cve_count, status (PkgStatus), install_ts, use_count.
`feature_vector()` → float32[8] for ML use (size, popularity, recency, security, etc.)

#### `DEFAULT_PACKAGES` — 30 packages

dev (10): python3, gcc, git, vim, neovim, nodejs, rust, docker, kubectl, make
data (6): jupyter, pandas, numpy, matplotlib, tensorflow, pytorch
system (6): htop, curl, wget, openssh, ufw, fail2ban
media (3): ffmpeg, vlc, gimp
comm (2): thunderbird, signal-cli
utility (5): zstd, ripgrep, fzf, tmux, containerd

#### `DependencyResolver`
BFS from target package. Detects cycles. Detects conflicts (if requested pkg conflicts
with an installed pkg). Detects missing deps (not in DB).
`_topological_sort(names)`: DFS post-order for correct install sequence.
Returns {install_order, count, total_size_mb, conflicts, missing, ok}.

#### `PackageHealthScorer`
Weights: freshness 30%, security 35%, popularity 20%, size 15%.
freshness = `max(0, 100 - last_updated_days × 0.3)`
security = `100` if no CVE; `max(0, 70 - cve_count×20)` if has CVE
popularity = `log1p(install_count) / log1p(10_000_000) × 100`
size_score = `max(0, 100 - size_kb / 10000)`
Grades: A≥85, B≥70, C≥55, D<55.

#### `InstallPatternLearner`
`_co_occur`: defaultdict(Counter). Item-item co-occurrence matrix.
`record_install(pkg, categories, currently_installed)`: increments co-occurrence for all pairs.
`record_session(installed_set)`: bulk update.
Seeded at init with 5 synthetic sessions (dev stack, data science, ops, security, media).
`recommend_from_installed(installed, db, top_k)`: sum co-occurrence for uninstalled candidates.

#### `NeuralPkgManager`
`install(name, dry_run)`: resolve deps → score health → mark installed → record in learner → append history.
`remove(name)`: check reverse deps first; fail if anything installed depends on it.
`search(query, top_k)`: word-overlap score on name+description+categories. Fuzzy fallback.
`recommend(context_mode, top_k)`: collaborative (0.5) + health/100 (0.3) + context_boost (0.2).
Context boost: +0.3 if package categories match mode keyword set.
`audit()`: score all installed, flag CVEs and grades below threshold, return recommendations.
`stats()`: {installed, available, install_history, context_mode, installed_list}.

---

### 5.7 `nos/system.py` (268 lines)

#### `NeuralNode`
`__init__(node_id)`: instantiates all 8 subsystems, calls `_bootstrap_fs()`,
sets `_next_pid=1000`, `_event_log=deque(500)`.

`_bootstrap_fs()`: indexes 7 sample files covering code, document, config, log, data,
shell config, and notes.

`run_command(natural_cmd)` — full dispatch table:
1. anomaly/diagnose/fix/heal/why is/what is wrong → `ConversationalDiagnostics.chat()`
2. find/search/locate/where is → `SemanticFileSystem.semantic_search()` with re.sub prefix strip
3. install * → `NeuralPkgManager.install()`
4. remove * → `NeuralPkgManager.remove()`
5. recommend/suggest packages → `NeuralPkgManager.recommend(context.current_mode)`
6. search packages/pkg search → `NeuralPkgManager.search()`
7. memory/compress/ram → `TieredMemoryManager.memory_report()`
8. cache → `PredictiveCache.cache_report()`
9. predict/forecast → `ResourcePredictor.predict()`
10. status/dashboard/overview → `NeuralNode.dashboard()`
11. spawn * → `NeuralNode.spawn_process()`
12. fallback → `{type:'unknown', hint: ...}`

`simulate_activity(n_ticks)`: sinusoidal CPU/RAM with Gaussian noise.
Feeds predictor, anomaly detector, context engine, file system, cache, diagnostics.
Updates diagnostics with `SystemSnapshot(federated_round=tick//10)`.

`dashboard()`: aggregates memory_report + cache_report + predictor.predict() +
context_summary + pkg.stats + anomaly.baseline_summary + fs.stats.

#### `NeuralOSNetwork`
N `NeuralNode` instances. `run_full_simulation(rounds, ticks_per_round)`.
Federated exchange is a stub comment — real implementation: §8.4.

---

## 6. OS-Layer Binaries & Configuration

### `/usr/bin/nos-init` (317 lines)
Boot sequence:
1. Clear screen, print ASCII NeuralOS banner
2. Load `/etc/nos/version.json`, `/var/lib/nos/state.json`
3. Try importing `nos.kernel.nn_core.MLP` (neural kernel verification)
4. Start 4 `ServiceDaemon` threads: anomaly (10s), monitor (5s), cache (30s), trainer (3600s once)
5. Increment and save `boot_count` to state.json
6. Print "NeuralOS ready."
7. `os.execv('/usr/bin/nos-shell', [...])` — hands off session

On SIGTERM: `_shutdown.set()` → each ServiceDaemon checks event and returns → log shutdown → exit 0.

`ServiceDaemon(threading.Thread)`: daemon=True, `_running` flag, calls `_fn()` every `_interval` seconds
using `_shutdown.wait(interval)` (wakes immediately on shutdown signal).

### `/usr/bin/nos-shell` (755 lines)
`setup_history()`: readline maxlen=2000, reads `~/.nos_history`, atexit write-back.
`build_prompt()`: `user@host cwd [mode]\nλ ` — context mode from `_node` if loaded.
Includes git branch via `git branch --show-current` with 0.5s timeout.

`nos_completer(text, state)`: completes NOS_COMMANDS list + PATH executables (os.listdir on PATH dirs).
`readline.set_completer(nos_completer)` + `parse_and_bind('tab: complete')`.

Main loop: `input(build_prompt())` → strip → dispatch:
1. exit/logout/quit → break
2. `!cmd` → raw subprocess
3. `cd *` → os.chdir
4. BUILTINS dict → `cmd_*(args)`
5. DIAG_KEYWORDS (`diagnose`, `fix`, `explain`, `heal`, `why`, `what`, `repair`, `issue`, `error`, `slow`, `broken`) → `NeuralNode.run_command()`
6. subprocess fallback

`_render_result(result, node)`: 12 render paths. Types handled:
diagnostic, file_search, pkg_install, pkg_remove, pkg_recommend, pkg_search,
memory_report/memory, cache_report/cache, resource_forecast, dashboard, process_spawn, fallback.

Shell builtins (22): help, version, uptime, services, neofetch, clear, status/dashboard,
find, search, index, install, remove, recommend, audit, pkg-list, memory, cache,
predict/forecast, anomaly, spawn, ps.

### `/usr/bin/nos` (135 lines)
Creates `NeuralNode`, calls `simulate_activity(5)`, maps argv to `run_command()`.
`--json` flag → `json.dumps(result, indent=2, default=str)`.
17 supported subcommands. Exits 1 on install/remove failure for scripting use.

### `/usr/bin/nos-login` (69 lines)
Prints OS banner + kernel version. Checks `NOS_AUTO_LOGIN`.
If 1: auto-login as `NOS_DEFAULT_USER`. If 0: interactive prompt (no PAM yet).
Sets USER, LOGNAME, HOME, SHELL, TERM, PYTHONPATH, NOS_VERSION, PATH.
`os.execv('/usr/bin/nos-shell', [...])`.

### `/usr/bin/nos-sysinfo` (114 lines)
ASCII NOS logo + right-column key-value display.
Reads /proc/uptime, /proc/loadavg, /proc/version. psutil for CPU count, memory.
Reads /etc/nos/version.json and /var/lib/nos/state.json for boot count + install date.
Ends with 8-colour ANSI palette strip.

---

## 7. Build & Container System

### Dockerfile — three stages

**Stage 1 `nos-base`** (`archlinux:base-devel`):
`pacman -Syu` then install 24 packages:
python, python-pip, python-numpy, python-rich, python-psutil, sudo, bash, coreutils,
util-linux, procps-ng, iproute2, less, man-db, which, htop, neofetch, tree, git, vim,
nano, curl, wget, jq, lz4, zstd, openssh, shadow, systemd.
Cache wiped after install.

**Stage 2 `nos-runtime`** (`nos-base`):
`pip install` (break-system-packages): prompt_toolkit, pydantic, msgpack, click.
Creates all FHS dirs. COPY rootfs trees. chmod +x all nos-* binaries.
Groups: `nos`, `nosadmin`. System user `nos` (r, g=nos, G=nosadmin+wheel).
Interactive user `user` (m, G=wheel+nos+nosadmin, shell=nos-shell, pw=neurlos).
Writes `.pth` file in site-packages: `/usr/lib/nos`.

**Stage 3 `nos-full`** (`nos-runtime`):
Copies os-release. Writes version.json with build date.
Python init: creates state.json (boot_count=0, install_date, node_id, models_trained=0, federated_round=0)
and packages.json (installed=[], history=[]).
Sets /etc/hostname=neurlos, /etc/hosts, /etc/locale.conf, locale-gen, /etc/localtime=UTC, /etc/issue.
`ENTRYPOINT ["/usr/bin/nos-init"]`

### docker-compose.yml
`nos-primary`: image neurlos/neurlos:0.1.0, stdin_open+tty, 4 env vars (NODE_ID, AUTO_LOGIN,
DEFAULT_USER, TERM), 4 named volumes (nos-home, nos-data, nos-logs, nos-cache),
network nos-net 172.30.0.0/24.
`nos-peer-1`: same image, `profiles: [federated]` — only starts with `--profile federated`.

### build.sh (177 lines, 9 commands)
`build` → docker build --target nos-full --tag neurlos/neurlos:0.1.0 --progress=plain
`run` → docker run --name nos-primary -it --rm --env ... --volume ... ${IMAGE}
`nsh` → docker run --rm -it ... /usr/bin/nos-shell
`shell/bash` → docker exec -it nos-primary /bin/bash
`test` → docker run --rm ... python3 /usr/lib/nos/test_all.py
`status` → checks container + docker exec nos status
`logs` → cat /var/log/nos/init.log
`clean` → docker rm + rmi + volume rm (nos-home, nos-data, nos-logs, nos-cache)
`up/compose` → docker compose up --build

---

## 8. Planned Features: Scoped & Designed

### 8.1 PicoClaw — Minimal Tiling GUI Layer

An AI-native tiling window manager that activates when `NOS_GUI_ENABLED=true`.
"Pico" = minimal footprint. "Claw" = predictive grip — the WM holds your next window
ready before you ask for it.

**Core AI behaviours:**
- **Predictive layout:** `ContextEngine.current_mode` determines default tile arrangement.
  coding mode → editor left (70%) + terminal right (30%).
  data_analysis → notebook left (60%) + file browser right (40%).
- **Window prefetch:** `MarkovAccessPredictor` over window focus sequences. When you move
  toward a window (cursor direction, Alt+Tab), PicoClaw begins rendering it offscreen 200ms early.
- **Adaptive splits:** MLP trained on resize history (`[5, 16, 8, 1]`, lr=1e-3) predicts
  preferred column ratio for next session. Persisted to `~/.nos_wm_prefs`.
- **Smart workspace assignment:** SemanticFileSystem tags the focused window's working
  directory, assigns it to the semantically closest workspace.

**New directory:**
```
rootfs/usr/lib/nos/gui/
├── __init__.py
├── picoclaw.py          WM main loop, X11 via python-xlib, event dispatch
├── layout_engine.py     MLP layout predictor, mode→geometry mapping
├── window_predictor.py  Markov predictor over window sequences
├── compositor.py        Damage tracking, vsync, offscreen buffer pool
└── theme.py             Dark theme: #0a0a12 bg, #00d4ff accent, #7c3aed highlight
```

**Activation flow:**
`NOS_GUI_ENABLED=true` in nos.conf → `nos-init` starts `picoclaw.service` →
`picoclaw.py` starts X session → connects to `NeuralNode` via Unix socket for AI calls.

**Keybindings (all configurable in `/etc/nos/nos.conf`):**
```
Super+Enter          → new nos-shell terminal
Super+d              → AI command launcher (NOS Agent if enabled)
Super+Tab            → predicted-next window (pre-rendered)
Super+Shift+Tab      → previous window
Super+[1-9]          → workspace N
Super+Shift+[1-9]    → move focused window to workspace N
Super+[hjkl]         → focus direction (vim keys)
Super+Shift+[hjkl]   → resize
Super+r              → AI-suggested resize ratio
Super+Shift+q        → kill focused window
Super+f              → fullscreen toggle
Super+space          → floating toggle
```

**systemd unit:** `picoclaw.service`, `PartOf=nos.target`, started only when
`NOS_GUI_ENABLED=true` (checked via `ConditionPathExists=/etc/nos/gui.enabled`).

---

### 8.2 NOS Agent — Agentic AI Shell

An autonomous agent that accepts multi-step goals in plain English and executes them
using OS tools with a plan → act → observe → adjust loop.

**Architecture:**
```
User goal: "set up a Python Flask API with redis, start it, and monitor it"
                          │
                          ▼
             NOSAgent.run(goal, max_steps=20)
                          │
         ┌────────────────┼──────────────────┐
         ▼                ▼                  ▼
      Planner          Executor           Observer
   goal→step list    run one step      health check
   MLP policy        capture output    after each step
   [64, 128, 64,     retry on fail     AnomalyDetector
    n_actions]       timeout 30s       ResourcePredictor
                                       rollback trigger
         │                │                  │
         └────────────────┼──────────────────┘
                          ▼
                       Memory
                short-term: context deque(20)
                long-term:  /var/lib/nos/agent/history.jsonl
                            embeddings via SemanticFileSystem
```

**Tool Registry (all available to agent):**
```python
shell(cmd: str) → {stdout, stderr, returncode}
file_write(path: str, content: str) → {ok, path}
file_read(path: str) → {ok, content}
file_append(path: str, line: str) → {ok}
nos_cmd(cmd: str) → NeuralNode.run_command(cmd) result
pkg_install(name: str) → NeuralPkgManager.install(name)
wait(seconds: float) → sleep
observe() → SystemSnapshot from current diagnostics
grep(pattern: str, path: str) → matching lines
env_get(key: str) → os.environ value
http_get(url: str) → response text (requires curl)
```

**Safety model (non-negotiable):**
- Agent never writes to `/etc/`, `/usr/`, `/sys/`, `/proc/` without `--allow-system`
- All shell commands run as `user` (not root) unless `--privileged`
- Destructive commands (rm, mv, chmod system files) require user confirmation
- Max steps enforced hard: raises `AgentMaxStepsError` at `NOS_AGENT_MAX_STEPS`
- On critical anomaly during execution: pause, notify user, await instruction
- All actions logged to `/var/lib/nos/agent/history.jsonl`

**Shell integration:**
```bash
# New builtin in nos-shell:
agent "set up nginx with SSL"
agent "migrate my postgres database to the new server"
agent "find all large files older than 30 days and archive them"

# Via nos CLI:
nos agent "compile and run my go project"
```

**New config keys:**
```
NOS_AGENT_ENABLED=true
NOS_AGENT_MAX_STEPS=20
NOS_AGENT_SANDBOX=true
NOS_AGENT_CONFIRM_DESTRUCTIVE=true
NOS_AGENT_HISTORY=/var/lib/nos/agent/history.jsonl
NOS_AGENT_TIMEOUT_PER_STEP=30
```

**New directory:**
```
rootfs/usr/lib/nos/agent/
├── __init__.py
├── nos_agent.py         NOSAgent class, run(goal) loop, step execution
├── planner.py           goal→[steps] decomposition, MLP action policy
├── tool_registry.py     @tool decorator, all tool implementations
├── executor.py          step runner with timeout, retry, capture
├── observer.py          post-step health check, rollback trigger
├── memory.py            context window, jsonl persistence, semantic search
└── rollback.py          filesystem snapshot, state restore on failure
```

---

### 8.3 nos-kernel-native — Real Kernel Module

A Linux kernel module (`nos.ko`) that bridges the Python AI layer to real kernel internals.

**Scope for v1.0:**
```
/proc/nos/
├── scheduler        AI writes priority hints (pid:nice_delta), kernel reads on next tick
├── memory           Real page access bitmap exposed to Python via read()
└── anomaly          AI writes alerts; kernel can throttle suspicious processes via SIGSTOP
```

`/dev/nos_ctl` character device: `ioctl` interface for:
- `NOS_IOCTL_SET_PRIORITY(pid, delta)` — adjusts scheduling priority
- `NOS_IOCTL_GET_PAGE_STATS(pid)` — returns page fault count + working set size
- `NOS_IOCTL_SANDBOX(pid, flags)` — applies namespace restrictions

**Build integration:**
```
kernel_module/
├── nos_main.c       module_init/exit, proc filesystem creation
├── nos_proc.c       /proc/nos/ read/write handlers
├── nos_sched.c      task_struct manipulation for priority hints
├── nos_mem.c        page access statistics collection
├── Kbuild
└── Makefile
```

---

### 8.4 Federated Gradient Sync (Real Network)

Replaces the stub in `NeuralOSNetwork` with a real distributed gradient exchange.

**Protocol per node, every `NOS_FEDERATED_SYNC_INTERVAL` seconds:**
1. `local_grads = node.compute_gradients()` — extract weight deltas since last sync
2. `DP.clip_and_noise(grads, epsilon=NOS_FEDERATED_DP_EPSILON)` — Gaussian mechanism
3. `POST http://peer:7700/gradients` with gzipped gradient payload (Ed25519 signed)
4. Collect responses from all reachable peers
5. `FedAvg(local_grads, [peer_grads])` — weighted average by data volume
6. `node.apply_gradients(averaged)` — update model weights
7. `PoLValidator.validate(before_loss, after_loss, grads)` — reject if loss didn't improve

**Differential Privacy:** Gaussian mechanism with sensitivity clipping. Each gradient
vector clipped to L2 norm ≤ C, then Gaussian noise N(0, σ²) added.
σ = C × √(2 × ln(1.25/δ)) / ε.

**New directory:**
```
rootfs/usr/lib/nos/federated/
├── __init__.py
├── federated_learning.py    FederatedAggregator (FedAvg), DifferentialPrivacy
├── proof_of_learning.py     LearningProof, PoLValidator, DAGLedger (chain of proofs)
├── gradient_server.py       aiohttp server on port 7700
├── gradient_client.py       async HTTP client, peer management
└── peer_registry.py         reads /etc/nos/peers.conf, health checks
```

**docker-compose** already has `nos-peer-1` with `--profile federated` and `nos-net`.
Peers communicate via `nos-net` bridge on 172.30.0.0/24.

---

### 8.5 Model Persistence Layer

Saves all trained model weights to `/var/lib/nos/models/` on shutdown.
Reloads on boot — eliminates cold-start synthetic training.

**Storage layout:**
```
/var/lib/nos/models/
├── resource_predictor_cpu.npz      MLP weights (layer_0_W, layer_0_b, ...)
├── resource_predictor_mem.npz
├── anomaly_encoder.npz
├── anomaly_decoder.npz
├── pattern_codebook.json           NeuralPatternPredictor top-512 patterns
├── markov_transitions.msgpack      MarkovAccessPredictor transition table
├── context_mode_scores.json        ContextEngine EMA state
└── pkg_cooccurrence.msgpack        InstallPatternLearner co-occurrence matrix
```

**API additions to MLP:**
```python
def save(self, path: str):
    params = {f'layer_{i}_{k}': v
              for i, p in enumerate(self.get_all_params())
              for k, v in p.items()}
    np.savez_compressed(path, **params)

def load(self, path: str) -> bool:   # returns False if shapes mismatch
    data = np.load(path)
    # reconstruct params list and call set_all_params()
```

**Boot sequence addition in nos-init:**
After services start: `ModelLoader.load_all(node, '/var/lib/nos/models/')`.
On SIGTERM: `ModelLoader.save_all(node, '/var/lib/nos/models/')`.

**New file:** `nos/kernel/model_persistence.py` — `ModelLoader` class.

---

### 8.6 nos-pacman — Real Package Manager Integration

Wraps real `pacman` as install backend while keeping the AI scoring layer on top.

**New file:** `nos/pkg_manager/pacman_bridge.py`
```python
class PacmanBridge:
    def install(self, name: str) -> dict    # subprocess pacman -S --noconfirm name
    def remove(self, name: str) -> dict     # subprocess pacman -R --noconfirm name
    def search(self, query: str) -> list    # pacman -Ss query → parsed list
    def info(self, name: str) -> dict       # pacman -Si name → parsed dict
    def sync(self) -> None                  # pacman -Sy
    def get_installed(self) -> Set[str]     # pacman -Q → names set
    def check_updates(self) -> List[str]    # pacman -Qu → names list
```

**Modified `NeuralPkgManager.install()`:**
```python
if NOS_PKG_BACKEND == 'pacman':
    health = self.scorer.score(pkg)
    if health['overall'] < NOS_PKG_HEALTH_THRESHOLD:
        # warn user, require confirmation
    result = PacmanBridge().install(name)
    self._record_install(name)
    return {**result, 'health_score': health}
```

**Config:** `NOS_PKG_BACKEND=internal` (default for container) / `pacman` (bare-metal).

---

### 8.7 Behavioural Auth — pam_nos.so

A PAM module authenticating users by behavioural fingerprint in addition to password.
Observes typing cadence, command patterns, and working hours.

**Flow:**
1. `pam_nos.so` (C) receives username from PAM stack
2. Calls Python daemon via Unix socket `/run/nos/auth.sock`
3. Daemon runs MLP `[8, 32, 16, 1]` over behaviour features
4. Returns auth_score (0.0–1.0) → PAM success if score > `NOS_AUTH_SCORE_THRESHOLD`

**Behaviour features (8):** typing_wpm, avg_command_length, command_diversity,
session_hour_norm, session_day_norm, error_rate, sudo_frequency, idle_ratio.

**New files:**
```
rootfs/usr/lib/nos/auth/
├── behaviour_auth.py    BehaviourProfiler (extracts features), AuthScorer (MLP)
└── nos_auth_daemon.py   Unix socket server

native/
└── pam_nos.c            C PAM module → socket call → auth response
```

**PAM config addition** `/etc/pam.d/nos-shell`:
```
auth    sufficient  pam_nos.so score_threshold=0.75
auth    required    pam_unix.so try_first_pass
```

---

### 8.8 /proc/nos — Virtual AI Filesystem

A FUSE filesystem exposing all AI subsystem state as readable virtual files.
Makes AI state scriptable from shell scripts without Python.

```
/proc/nos/                  (FUSE mount, owned by nos user)
├── status                  JSON: NeuralNode.dashboard()
├── version                 "NeuralOS 0.1.0 Synapse"
├── anomaly/
│   ├── score               "0.0234\n"
│   ├── threshold           "0.0891\n"
│   └── severity            "normal\n"
├── memory/
│   ├── hot_regions         "3\n"
│   ├── warm_regions        "7\n"
│   ├── cold_regions        "2\n"
│   └── compression_ratio   "2.34\n"
├── cache/
│   ├── hit_rate            "78.3\n"
│   ├── size_mb             "45.2\n"
│   └── prefetch_queue      "3\n"
├── predictor/
│   ├── cpu_forecast        "42.1,45.3,48.2,51.0,53.4\n"
│   └── mem_forecast        "61.2,62.0,62.5,63.1,63.8\n"
└── agent/
    ├── status              "idle\n"
    └── last_goal           "set up nginx\n"
```

**Implementation:** `nos/fs/procnos_fuse.py` using `fusepy`.
Reads from a shared `NeuralNode` instance (or IPC socket to nos-init).
Read-only except `/proc/nos/agent/` which accepts goal writes.

**New systemd unit:** `nos-procfs.service`, `ExecStart=python3 nos-procfs-daemon.py`.

---

### 8.9 nos-update — Rolling AI-verified Updates

Rolling update system where model weight updates must pass Proof of Learning validation
before being applied.

**Update flow:**
```
nos-update check
    ├── Fetch manifest from NOS_UPDATE_SERVER (HTTPS + Ed25519 signature)
    ├── Compare versions, skip if up to date
    ├── Download new weights bundle (.npz.gz + .sig)
    ├── Verify Ed25519 signature against bundled public key
    ├── PoLValidator: load new weights, measure validation loss
    │       only accept if new_loss < current_loss × 0.95
    ├── A/B shadow: run new model alongside current for 30 min
    │       log accuracy comparison to /var/log/nos/update_ab.log
    ├── If new wins: atomic swap (rename old → models/prev/, new → models/)
    └── On failure: keep prev/ as rollback, log to /var/log/nos/update.log
```

**New files:**
```
rootfs/usr/lib/nos/update/
├── update_manager.py    UpdateManager.check(), download(), verify(), apply(), rollback()
├── pol_verifier.py      PoLValidator, loss measurement on local validation set
├── ab_tester.py         ShadowTester, accuracy comparison, decision logic
└── manifest.py          UpdateManifest parser, Ed25519 verification via cryptography lib
```

**systemd timer:** `nos-update.timer` — `OnCalendar=daily`, triggers `nos-update.service`.

---

### 8.10 nos-sandbox — AI Process Isolation

Uses Linux namespaces + seccomp-bpf to sandbox processes flagged as anomalous,
and to isolate NOS Agent tool execution.

**Trigger flow:**
```python
# In _svc_anomaly_watchdog:
obs = anomaly_detector.observe(...)
if obs['severity'] == 'critical':
    pid = find_top_cpu_process()
    sandbox = NOSSandbox(pid)
    sandbox.apply(namespaces=['net', 'pid', 'ipc'],
                  seccomp_profile='restrictive')
    node.diagnostics.log_event('SANDBOX_APPLIED', pid=pid)
```

**Namespace isolation options:**
- `net`: new network namespace (no internet, only loopback)
- `pid`: new PID namespace (process can't see others)
- `ipc`: new IPC namespace (no shared memory with outside)
- `user`: new user namespace (remaps to unprivileged)

**Seccomp profiles:**
- `restrictive`: allow only basic I/O syscalls, block execve, network calls, mmap(EXEC)
- `standard`: NeuralOS default (block ptrace, perf_event_open, kexec)
- `permissive`: logging only, no actual blocking

**New file:** `nos/sandbox/nos_sandbox.py`

---

## 9. Final Build Target: v1.0.0 Cortex

### Complete feature matrix

| Feature | v0.1.0 | v1.0.0 |
|---|---|---|
| Neural kernel primitives (MLP, AE) | ✅ | ✅ |
| Semantic filesystem | ✅ | ✅ + FUSE /proc/nos |
| Anomaly detection | ✅ | ✅ + sandbox trigger |
| Resource prediction | ✅ | ✅ + real /proc feed |
| Neural memory compression | ✅ | ✅ + persisted weights |
| Predictive file cache | ✅ | ✅ + persisted Markov |
| Conversational diagnostics | ✅ | ✅ + 15+ issues |
| AI package manager | ✅ | ✅ + pacman backend |
| nos-init + nos-shell + nos CLI | ✅ | ✅ |
| Docker container | ✅ | ✅ + bootable ISO |
| systemd services | ✅ | ✅ + nos-update.timer |
| PicoClaw WM | ❌ | ✅ §8.1 |
| NOS Agent | ❌ | ✅ §8.2 |
| Kernel module nos.ko | ❌ | ✅ §8.3 |
| Real federated sync | ❌ | ✅ §8.4 |
| Model persistence | ❌ | ✅ §8.5 |
| pacman bridge | ❌ | ✅ §8.6 |
| Behavioural PAM auth | ❌ | ✅ §8.7 |
| /proc/nos FUSE | ❌ | ✅ §8.8 |
| Rolling AI-verified updates | ❌ | ✅ §8.9 |
| AI process sandboxing | ❌ | ✅ §8.10 |

### v1.0.0 full directory additions

```
rootfs/usr/lib/nos/
├── agent/          §8.2 — NOSAgent, Planner, ToolRegistry, Executor, Memory
├── auth/           §8.7 — BehaviourProfiler, AuthScorer, auth daemon
├── federated/      §8.4 — FedAvg, DP, PoL, gradient server/client
├── fs/             §8.8 — FUSE /proc/nos implementation
├── gui/            §8.1 — PicoClaw WM, LayoutEngine, WindowPredictor
├── sandbox/        §8.10 — NOSSandbox, namespace + seccomp control
└── update/         §8.9 — UpdateManager, PoLVerifier, A/B Tester

kernel_module/      §8.3 — nos.ko C source
native/             §8.7 — pam_nos.c
```

### New pacman packages to add to Dockerfile for v1.0.0

```
python-fuse  fusepy         # /proc/nos FUSE (§8.8)
python-xlib  python-pygame  # PicoClaw WM (§8.1)
wayland  python-pywayland   # Wayland session support
linux-headers               # kernel module build (§8.3)
grpc  python-grpcio         # federated sync (§8.4)
python-cryptography         # update signatures (§8.9)
libpam  pam                 # PAM module (§8.7)
```

### Test suite target for v1.0.0

Target: 200+ tests. Current: 83/83.

New sections to add:
```
Section 16: PicoClaw layout predictor (mode → geometry mapping)
Section 17: NOS Agent tool execution (mock subprocess)
Section 18: NOS Agent rollback on anomaly trigger
Section 19: Federated gradient sync (2-node mock exchange)
Section 20: Model persistence round-trip (save → reload → predict matches)
Section 21: pacman bridge (mock subprocess.run)
Section 22: /proc/nos FUSE read (mount + read score)
Section 23: Behavioural auth scoring (train + authenticate)
Section 24: Sandbox apply + release (namespace flags)
Section 25: Rolling update PoL verification (good update accepted, bad rejected)
```

---

## 10. Extension Recipes

### Add a new AI subsystem

1. `rootfs/usr/lib/nos/nos/<name>/<module>.py` + `__init__.py`
2. Instantiate in `NeuralNode.__init__()`:
   ```python
   from nos.<name>.<module> import MyClass
   self.mysubsys = MyClass()
   ```
3. Add dispatch to `NeuralNode.run_command()`:
   ```python
   if 'mycommand' in cmd:
       return {'type': 'my_type', **self.mysubsys.do_thing()}
   ```
4. Add render to `nos-shell._render_result()`:
   ```python
   elif rtype == 'my_type':
       print(f"  {result}")
   ```
5. Add `ServiceDaemon` to `nos-init` if background loop needed
6. Add section to `test_all.py`

### Add a diagnostic issue

Append to `ISSUE_KB` in `conversational_diagnostics.py`:
```python
Issue(
    id='MY_ISSUE',
    title='Short human-readable title',
    severity=Severity.WARNING,         # INFO | WARNING | ERROR | CRITICAL
    description='What is happening.',
    symptoms=['cpu > 85'],             # keys evaluated in SymptomMatcher._score_issue
    root_causes=['Cause A', 'Cause B'],
    fixes=['nos do-something', 'kill -9 suspect_pid'],
    auto_fixable=True,
    affected_component='Subsystem Name',
)
```
To add a new symptom key (e.g. `'gpu > 90'`): add to `SymptomMatcher._score_issue()`
checks dict and add `gpu_pct: float = 0.0` to `SystemSnapshot`.

### Add a shell builtin

```python
def cmd_mycommand(args):
    node = get_node()
    result = node.run_command('mycommand ' + ' '.join(args))
    _render_result(result, node)

BUILTINS['mycommand'] = cmd_mycommand
NOS_COMMANDS.append('mycommand')     # for tab completion
```

### Add a package

In `neural_pkg_manager.py`, append to `DEFAULT_PACKAGES`:
```python
Package(
    'pkgname', '1.0.0', 'One-line description',
    ['category'],           # dev | data | ops | security | media | utility
    depends=['python3'],    # names of other packages in DEFAULT_PACKAGES
    conflicts=[],
    size_kb=5000,
    install_count=500_000,
    last_updated_days=14,
    has_cve=False, cve_count=0,
)
```

### Add a NOS Agent tool (v1.0)

In `nos/agent/tool_registry.py`:
```python
@tool('tool_name')
def my_tool(param1: str, param2: int = 0) -> dict:
    """One-line description (shown to planner)."""
    result = do_something(param1, param2)
    return {'success': True, 'output': str(result)}
```
Tools auto-register. The planner sees name + docstring when deciding which tool to call.

---

## 11. Runtime State & Log Files

| Path | Format | Created by | Contents |
|---|---|---|---|
| `/var/lib/nos/state.json` | JSON | nos-init | boot_count, install_date, node_id, models_trained, federated_round |
| `/var/lib/nos/packages.json` | JSON | Dockerfile init | installed[], history[] |
| `/var/lib/nos/models/` | .npz + .json + .msgpack | nos-trainer [v1.0] | all model weights |
| `/var/lib/nos/agent/history.jsonl` | JSONL | NOS Agent [v1.0] | {ts, goal, step, tool, result} per line |
| `/var/log/nos/init.log` | text | nos-init | [HH:MM:SS] [LEVEL] message |
| `/var/log/nos/shell.log` | text | nos-shell | every command entered |
| `/var/log/nos/anomaly.log` | text | nos-anomaly service | score, severity, timestamp |
| `/var/log/nos/resources.log` | text | nos-resource-monitor | `<ts> cpu=XX mem=XX` |
| `/var/log/nos/trainer.log` | text | nos-trainer | training completion |
| `/var/log/nos/update.log` | text | nos-update [v1.0] | update check + apply results |
| `/var/log/nos/update_ab.log` | text | nos-update [v1.0] | A/B model comparison |
| `/etc/nos/version.json` | JSON | Dockerfile | name, version, codename, base, arch, build_date |
| `/etc/nos/nos.conf` | KEY=VALUE | static | all tunable config |
| `/etc/nos/peers.conf` | text [v1.0] | user | one IP:port per line |
| `~/.nos_history` | readline | nos-shell | last 2000 commands |
| `~/.nosrc` | bash | /etc/skel | user shell customisations |
| `~/.nos_wm_prefs` | JSON [v1.0] | PicoClaw | learned split ratios |
| `~/.nos_auth_profile` | JSON [v1.0] | pam_nos | behavioural fingerprint |

---

## 12. Configuration Reference: /etc/nos/nos.conf

All values are bash KEY=VALUE, exported by `/etc/profile.d/nos.sh`,
read by Python modules via `os.environ.get('KEY', default)`.

| Key | Default | Module |
|---|---|---|
| NOS_NODE_ID | nos-primary | NeuralNode, nos-init |
| NOS_HOSTNAME | neurlos | /etc/hostname |
| NOS_SCHEDULER_LR | 0.001 | NeuralScheduler (future) |
| NOS_SCHEDULER_RETRAIN_INTERVAL | 300 | NeuralScheduler (future) |
| NOS_MEM_HOT_LIMIT_MB | 512 | TieredMemoryManager |
| NOS_MEM_WARM_LIMIT_MB | 1024 | TieredMemoryManager |
| NOS_MEM_COMPRESS_LEVEL | 3 | _compress_to_warm |
| NOS_CACHE_MAX_MB | 128 | PredictiveCache |
| NOS_CACHE_COMPRESS | true | PredictiveCache |
| NOS_CACHE_MARKOV_ORDER | 2 | MarkovAccessPredictor |
| NOS_ANOMALY_SIGMA | 3.0 | AnomalyDetector._update_threshold |
| NOS_ANOMALY_WINDOW | 200 | AnomalyDetector (deque maxlen) |
| NOS_ANOMALY_TRAIN_INTERVAL | 10 | AnomalyDetector.observe |
| NOS_PREDICTOR_WINDOW | 30 | ResourcePredictor |
| NOS_PREDICTOR_HORIZON | 5 | ResourcePredictor |
| NOS_FEDERATED_ENABLED | true | NeuralOSNetwork |
| NOS_FEDERATED_DP_EPSILON | 1.0 | DifferentialPrivacy (v1.0) |
| NOS_FEDERATED_DP_DELTA | 1e-5 | DifferentialPrivacy (v1.0) |
| NOS_FEDERATED_SYNC_INTERVAL | 3600 | FederatedAggregator (v1.0) |
| NOS_FEDERATED_PEERS | /etc/nos/peers.conf | peer_registry (v1.0) |
| NOS_FEDERATED_PORT | 7700 | gradient_server (v1.0) |
| NOS_SHELL | /usr/bin/nos-shell | nos-login |
| NOS_DEFAULT_USER | user | nos-login, nos-init |
| NOS_AUTO_LOGIN | 1 | nos-login |
| NOS_LOG_LEVEL | INFO | all daemons |
| NOS_LOG_DIR | /var/log/nos | all daemons |
| NOS_LOG_MAX_MB | 50 | log rotation (v1.0) |
| NOS_PKG_HEALTH_THRESHOLD | 60 | NeuralPkgManager |
| NOS_PKG_AUTO_RECOMMEND | true | nos-shell post-install |
| NOS_PKG_BACKEND | internal | NeuralPkgManager (v1.0: pacman) |
| NOS_GUI_ENABLED | false | PicoClaw (v1.0) |
| NOS_GUI_WM | nos-wm | PicoClaw (v1.0) |
| NOS_GUI_SCALE | 1.0 | PicoClaw (v1.0) |
| NOS_AGENT_ENABLED | true | NOSAgent (v1.0) |
| NOS_AGENT_MAX_STEPS | 20 | NOSAgent (v1.0) |
| NOS_AGENT_SANDBOX | true | NOSAgent + NOSSandbox (v1.0) |
| NOS_AGENT_CONFIRM_DESTRUCTIVE | true | NOSAgent (v1.0) |
| NOS_AGENT_HISTORY | /var/lib/nos/agent/history.jsonl | NOSAgent (v1.0) |
| NOS_AGENT_TIMEOUT_PER_STEP | 30 | Executor (v1.0) |
| NOS_AUTH_BEHAVIOUR | false | pam_nos (v1.0) |
| NOS_AUTH_SCORE_THRESHOLD | 0.75 | AuthScorer (v1.0) |
| NOS_SANDBOX_AUTO | true | nos-anomaly service (v1.0) |
| NOS_SANDBOX_NAMESPACES | net,pid | NOSSandbox (v1.0) |
| NOS_UPDATE_AUTO | false | nos-update timer (v1.0) |
| NOS_UPDATE_SERVER | https://update.neurlos.io | UpdateManager (v1.0) |
| NOS_UPDATE_VERIFY_POL | true | PoLVerifier (v1.0) |

---

## 13. Testing

### Running the test suite

```bash
# Inside container:
PYTHONPATH=/usr/lib/nos python3 /usr/lib/nos/test_all.py

# Via build.sh:
./build.sh test

# Directly from repo (needs numpy, psutil):
cd rootfs/usr/lib && PYTHONPATH=. python3 nos/test_all.py
```

Expected output: `Passed : 83/83  (100.0%)`

### Test suite structure (15 sections, 83 tests)

| # | Module under test | What's covered |
|---|---|---|
| 1 | SemanticFileSystem | index_file, semantic_search scoring, recency boost, hot_files, stats |
| 2 | AnomalyDetector | observe returns expected keys, score in range, baseline after training |
| 3 | ResourcePredictor | record + predict, forecast shape [5], values in [0,100], spike_warning |
| 4 | ContextEngine | mode detection (coding/data/ops), context_summary, prefetch_tags |
| 5 | DeltaEncoder | keyframe on first call, delta on repeat, round-trip correctness, sparsity threshold |
| 6 | TieredMemoryManager | store→access round-trip, report keys, hot/warm/cold counts, eviction |
| 7 | MarkovAccessPredictor | record sequence, predict_next returns correct path at top |
| 8 | PredictiveCache | get miss, put+get hit, hit_rate numerics, eviction on full, prefetch queue |
| 9 | SymptomMatcher | normal snapshot → 0 issues, stressed snapshot → issues detected, specific IDs |
| 10 | ConversationalDiagnostics | diagnose cmd, explain N, fix all, cpu component, history |
| 11 | DependencyResolver | single install, auto-deps pulled in, duplicate ignored, remove, reverse-dep block |
| 12 | PackageHealthScorer | healthy>unhealthy ordering, A/B grades for good pkg, C/D for CVE+old |
| 13 | NeuralPkgManager | search, recommend excludes installed, audit flags CVE |
| 14 | NeuralNode | dashboard keys, find returns results, install ok, diagnose type, memory keys |
| 15 | NeuralOSNetwork | 2-node construction, simulate, both dashboards accessible |

---

## 14. Known Constraints & Intentional Decisions

| Constraint | Rationale | Upgrade path |
|---|---|---|
| Pure NumPy, no PyTorch | Runs on mid-range hardware without GPU. No 2 GB dependency. Container pulls in seconds. | Replace MLP internals with ONNX runtime as optional backend for v1.0 GPU mode. All model classes have `get_all_params()` / `set_all_params()` to swap backends without API change. |
| Hash-based embeddings (not word2vec) | Zero training data at install time. Deterministic. <1ms per file. Sufficient for tag-based search. | Replace `_hash_embed` in `ai_services.py` with a real sentence encoder (e.g. all-MiniLM via ONNX). API is identical — callers don't change. |
| Markov order-2 (not transformer) | O(1) lookup, no GPU, no training data. Sufficient for file access prediction. | Train a small LSTM on `/var/log/nos/shell.log` after 30 days. `predict_next()` API unchanged. |
| 30-package internal DB (not pacman) | Self-contained for container demo. AI scoring layer is backend-agnostic. | Add `PacmanBridge` (§8.6). `NeuralPkgManager.install()` already designed with backend abstraction. |
| No PAM in container | Docker auto-login is appropriate for containers. | `pam_nos.so` (§8.7) for bare-metal. `/etc/pam.d/nos-shell` is already the correct config location. |
| systemd units present but not PID 1 | Docker doesn't use systemd as PID 1 in standard containers. `ServiceDaemon` threads replace them inside Docker. | Bare-metal: `systemctl enable nos.target` works immediately. Units are correct. |
| Models not persisted | `/var/lib/nos/models/` directory exists, ready. All models have `get_all_params()`. | `ModelLoader` (§8.5) is a single new file, ~100 lines. |
| No real kernel scheduler integration | Python-space priority hints only. No actual preemption. | `nos.ko` (§8.3) + `os.nice()` / `sched_setscheduler` calls from Python for near-term. Real kernel module for v1.0. |
| `_hash_embed` not geometrically semantic | 'dog' and 'puppy' have no cosine relationship. | Acceptable for file retrieval where tags+filename dominate. Use sentence-BERT for v1.0. |
| No network in container by default | Security: containers shouldn't have open ports by default. | Federated ports opened via `docker-compose.yml` when `--profile federated` is specified. |

---

## 15. Quick API Reference for AI Agents

```python
# ── Bootstrap ────────────────────────────────────────────────────────────────
import sys
sys.path.insert(0, '/usr/lib/nos')
from nos.system import NeuralNode, NeuralOSNetwork

node = NeuralNode('agent-node')
node.simulate_activity(n_ticks=20)  # required: seeds all ML models

# ── run_command — the universal interface ─────────────────────────────────────
# Returns {'type': str, ...} always.

r = node.run_command('status')                          # type: dashboard
r = node.run_command('find python configuration files') # type: file_search
r = node.run_command('install neovim')                  # type: pkg_install
r = node.run_command('remove vim')                      # type: pkg_remove
r = node.run_command('search packages database')        # type: pkg_search
r = node.run_command('recommend')                       # type: pkg_recommend
r = node.run_command('audit')                           # type: (dict with issues)
r = node.run_command('memory')                          # type: memory_report
r = node.run_command('cache')                           # type: cache_report
r = node.run_command('predict')                         # type: resource_forecast
r = node.run_command('diagnose')                        # type: diagnostic
r = node.run_command('fix all')                         # type: diagnostic
r = node.run_command('why is the system slow')          # type: diagnostic
r = node.run_command('spawn myprocess')                 # type: process_spawn

# ── SemanticFileSystem ────────────────────────────────────────────────────────
rec = node.fs.index_file('/path/report.pdf', 'quarterly finance report', ['finance','pdf'], 40000)
# rec.path, rec.tags, rec.embedding, rec.content_hash

results = node.fs.semantic_search('tax documents 2024', top_k=5, tag_filter='finance')
for score, rec in results:
    print(f"{score:.3f}  {rec.path}  {rec.tags}")

node.fs.record_access('/path/report.pdf')  # updates access_count + last_accessed
node.fs.hot_files(top_k=10)               # [(access_count, FileRecord)]
node.fs.stats()                            # {indexed_files, unique_tags, total_size_mb}

# ── AnomalyDetector ───────────────────────────────────────────────────────────
obs = node.anomaly.observe(
    syscall_counts={'read': 20, 'write': 5, 'open': 3, 'close': 3},
    cpu_pct=45.0, mem_pct=60.0,
    thread_count=30, uptime_s=3600
)
# obs = {score: float, threshold: float, anomaly: bool,
#        severity: 'normal'|'elevated'|'warning'|'critical', top_syscalls: dict}

node.anomaly.baseline_summary()
# {mean_error: float, std_error: float, threshold: float, samples: int}

# ── ResourcePredictor ─────────────────────────────────────────────────────────
node.predictor.record(cpu_pct=55.0, mem_pct=70.0)
fc = node.predictor.predict()
# {status: 'ok'|'insufficient_data', cpu_forecast: [f]*5, mem_forecast: [f]*5,
#  spike_warning: bool, spike_cpu: bool, spike_mem: bool,
#  horizon_seconds: 5, trained_steps: int}
node.predictor.recommend_action()   # str description or None

# ── ContextEngine ─────────────────────────────────────────────────────────────
node.context.record_event('process_start', 'python3')
node.context.record_event('file_access', '/home/user/data.csv')
node.context.current_mode              # 'coding'|'data_analysis'|'sysadmin'|...
node.context.context_summary()
# {mode, session_minutes, top_processes: Counter, mode_scores: dict}
node.context.suggested_prefetch_tags() # ['code', 'config', ...] for cache warm

# ── TieredMemoryManager ───────────────────────────────────────────────────────
node.compressor.store(pid=1234, region_id='heap', data=b'\x00'*1024*1024, region_type='heap')
data = node.compressor.access(pid=1234, region_id='heap')  # returns bytes or None
node.compressor.evict_lru(target_free_mb=128)
node.compressor.memory_report()
# {hot_regions, warm_regions, cold_regions, hot_mb, warm_mb, cold_mb,
#  total_original_mb, total_compressed_mb, overall_ratio, savings_mb,
#  delta_hits, neural_assists, avg_compress_ms, avg_decompress_ms}

# ── PredictiveCache ───────────────────────────────────────────────────────────
node.cache.put('/path/file.txt', b'content', tags=['text'], prefetch_score=0.8)
data = node.cache.get('/path/file.txt')   # None on miss, bytes on hit
node.cache.invalidate('/path/file.txt')
node.cache.get_prefetch_queue()           # [(score, path), ...] heapq sorted
node.cache.hot_paths(top_k=10)
node.cache.cache_report()
# {cached_files, cache_size_mb, max_size_mb, utilisation_pct,
#  hit_rate_pct, prefetch_hit_rate_pct, evictions, compression_savings_mb,
#  prefetch_queue_depth}

# ── ConversationalDiagnostics ─────────────────────────────────────────────────
from nos.diagnostics.conversational_diagnostics import SystemSnapshot
snap = SystemSnapshot(
    cpu_pct=92, mem_pct=88,
    anomaly_score=0.4, anomaly_severity='critical',
    cache_hit_rate=20, zombie_count=8,
    federated_round=1
)
node.diagnostics.update_snapshot(snap)
response = node.diagnostics.chat('diagnose', compressor=node.compressor, cache=node.cache)
# response is a multi-line formatted string

# ── NeuralPkgManager ─────────────────────────────────────────────────────────
r = node.pkg.install('git')
# {ok: bool, package: str, install_plan: {install_order, count, total_size_mb},
#  health_score: {overall, grade, flags}, error?: str, suggestions?: [str]}

r = node.pkg.remove('git')
# {ok: bool, package: str, error?: str, reverse_deps?: [str]}

results = node.pkg.search('database client', top_k=5)
# [{name, version, description, categories, installed: bool, score: float}]

recs = node.pkg.recommend(context_mode='data_analysis', top_k=8)
# [{name, version, health_grade, size_mb, reason: str, collaborative_score, health_score}]

audit = node.pkg.audit()
# {installed_count, avg_health, issues: [str], cve_packages: [str],
#  total_size_mb, recommendations: [str]}

node.pkg.stats()
# {installed: int, available: int, install_history: int,
#  context_mode: str, installed_list: [str]}

# ── NeuralNode full dashboard ─────────────────────────────────────────────────
d = node.dashboard()
# d.keys(): node_id, uptime_s, tick, context_mode,
#            memory (full memory_report),
#            cache (full cache_report),
#            resource_forecast (full predict result),
#            anomaly_baseline, packages, filesystem

# ── Process management ────────────────────────────────────────────────────────
pid = node.spawn_process('myapp', cpu_burst=100.0, mem_mb=256.0)
success = node.kill_process(pid)          # True if pid existed
events = node.event_log(n=20)            # last N {ts, msg} dicts

# ── Multi-node federated network ──────────────────────────────────────────────
net = NeuralOSNetwork(n_nodes=3)
net.run_full_simulation(rounds=2, ticks_per_round=30)
net.print_dashboard()                    # prints all 3 node dashboards
primary = net.nodes[0]                   # access individual NeuralNode
primary.dashboard()
```

---

*NeuralOS — the OS that learns with you.*  
*GEMINI.md is the single source of truth for every AI agent, contributor, and automated tool building on NeuralOS.*  
*When in doubt: the code is in `/usr/lib/nos/`. This file tells you where to look.*
