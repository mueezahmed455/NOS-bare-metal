# NeuralOS - AI is the OS

**Version:** 0.1.0 (Synapse)

NeuralOS is an AI-driven operating system where traditional OS heuristics are replaced by trained neural networks that learn from the machine they run on.

## Features

### Core AI Subsystems

- **Neural Kernel** - Pure NumPy MLP, Autoencoder, Attention layers
- **Semantic File System** - Hash-based embeddings for file search
- **Anomaly Detection** - Autoencoder-based system monitoring
- **Resource Prediction** - MLP-based CPU/memory forecasting
- **Context Engine** - Activity mode detection
- **Neural Memory Compressor** - Delta encoding + pattern prediction
- **Predictive Cache** - Markov + time-based prefetching
- **Conversational Diagnostics** - AI-powered troubleshooting
- **Neural Package Manager** - Collaborative filtering for packages

### Shell & CLI

```bash
# Interactive AI shell
nos-shell

# CLI commands
nos diagnose          # System diagnosis
nos status            # Dashboard
nos find <query>      # Semantic file search
nos install <pkg>     # Install package
nos memory            # Memory report
nos cache             # Cache statistics
nos predict           # Resource forecast
```

## Quick Start

### Build with Docker

```bash
# Build the image
./build.sh build

# Run tests
./build.sh test

# Run interactively
./build.sh run

# Start full stack with Docker Compose
./build.sh up
```

### Docker Compose (with federated learning)

```bash
# Start primary node
docker compose up -d

# Start with federated peer
docker compose --profile federated up -d

# View logs
docker compose logs -f
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│   nos-shell (TUI)  │  nos CLI  │  PicoClaw (GUI, planned)   │
├─────────────────────────────────────────────────────────────┤
│                    NEURAL NODE (system.py)                   │
│  run_command() · dashboard() · simulate_activity()          │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Semantic │ Anomaly  │ Resource │ Context  │ Neural Memory   │
│   FS     │ Detector │ Predictor│ Engine   │ Compressor      │
├──────────┴──────────┴──────────┴──────────┴─────────────────┤
│              KERNEL (nn_core.py) - Pure NumPy                │
│   DenseLayer · MLP · Autoencoder · AttentionLayer           │
├─────────────────────────────────────────────────────────────┤
│              Arch Linux · systemd · pacman                   │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
arch/
├── Dockerfile              # Multi-stage build
├── docker-compose.yml      # Orchestration
├── build.sh                # Build commands
├── rootfs/
│   ├── etc/
│   │   ├── nos/
│   │   │   └── nos.conf    # Configuration
│   │   └── profile.d/
│   │       └── nos.sh      # Environment
│   └── usr/
│       ├── bin/
│       │   ├── nos         # CLI tool
│       │   ├── nos-init    # PID 1
│       │   ├── nos-shell   # Login shell
│       │   └── nos-sysinfo # System info
│       └── lib/nos/
│           ├── kernel/         # Neural network core
│           ├── services/       # AI services
│           ├── compressor/     # Memory compression
│           ├── cache/          # Predictive cache
│           ├── diagnostics/    # Conversational diagnostics
│           ├── pkg_manager/    # Neural package manager
│           └── system.py       # NeuralNode integration
└── x86_64/                 # Native kernel (C++)
    ├── boot.asm            # Multiboot2 bootloader
    ├── arch.cpp/h          # Architecture layer
    ├── kernel.cpp/h        # Kernel entry point
    ├── console.cpp/h       # VGA output
    ├── memory.cpp/h        # Memory management
    └── linker.ld           # Linker script
```

## Configuration

Edit `/etc/nos/nos.conf`:

```ini
AUTO_LOGIN=true
DEFAULT_USER=user
NODE_ID=primary

# Memory compression
HOT_LIMIT_MB=512
WARM_LIMIT_MB=1024

# Cache
CACHE_MAX_MB=256

# Anomaly detection
ANOMALY_THRESHOLD=3.0
```

## Testing

```bash
# Run full test suite (83 tests)
./build.sh test

# Or directly in container
python3 /usr/lib/nos/test_all.py
```

## Roadmap to v1.0.0 (Cortex)

- [ ] PicoClaw GUI window manager
- [ ] NOS Agent (agentic AI shell)
- [ ] Real kernel module (nos.ko)
- [ ] Federated gradient sync
- [ ] Model weight persistence
- [ ] pacman integration
- [ ] PAM behavioral auth
- [ ] /proc/nos virtual filesystem
- [ ] AI process sandboxing

## License

MIT License

## Credits

NeuralOS is built on the principle that **AI is the OS** - not bolted on, but fundamental to every layer.
