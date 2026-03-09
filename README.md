# NeuralOS (C++ Version)

**A fully functional operating system written in C++ from the ground up.**

This is a complete rewrite of NeuralOS in C++ that boots on bare metal x86_64 hardware.

## Features

- **Bare Metal Kernel**: Boots directly on x86_64 hardware without any underlying OS
- **Memory Management**: Physical and virtual memory with paging
- **Process Scheduling**: Preemptive multitasking with round-robin scheduling
- **File System**: In-memory file system with inode-based structure
- **Neural Networks**: Built-in neural network processing with backpropagation
- **Federated Learning**: Distributed machine learning across nodes
- **Consensus Engine**: Proof-of-learning consensus mechanism
- **Command Shell**: Interactive shell with built-in commands
- **Interrupt Handling**: Complete x86_64 interrupt and exception handling
- **System Calls**: Kernel API for user-space programs

## Architecture

```
NeuralOS/
├── arch/x86_64/          # Architecture-specific code
│   ├── boot.asm         # Multiboot bootloader
│   ├── interrupts.asm   # Interrupt handlers
│   ├── arch.cpp         # CPU initialization
│   ├── gdt.cpp          # Global Descriptor Table
│   ├── idt.cpp          # Interrupt Descriptor Table
│   └── paging.cpp       # Virtual memory management
├── kernel/              # Core kernel
│   ├── main.cpp         # Kernel entry point
│   ├── kernel.cpp       # Core utilities
│   ├── console.cpp      # VGA text output
│   ├── memory.cpp       # Memory management
│   ├── scheduler.cpp    # Process scheduling
│   ├── filesystem.cpp   # File system
│   ├── neural_core.cpp  # Neural networks
│   ├── shell.cpp        # Command shell
│   └── [other modules]
├── include/             # Header files
└── CMakeLists.txt       # Build system
```

## Building

### Prerequisites

- CMake 3.16+
- GCC cross-compiler for x86_64-elf
- NASM assembler
- QEMU for testing

### Build Steps

```bash
# Create build directory
mkdir build
cd build

# Configure with CMake
cmake .. -DARCH=x86_64

# Build kernel
make

# Create bootable ISO
make iso
```

## Running

### In QEMU

```bash
# Run kernel directly
make run

# Run with debugging
make debug

# Run bootable ISO
qemu-system-x86_64 -cdrom neuralos.iso
```

### On Real Hardware

Burn the ISO to a USB drive and boot from it. NeuralOS will start automatically.

## Usage

Once booted, you'll see the NeuralOS prompt:

```
neuralos:/$ help
```

Available commands:
- `help` - Show available commands
- `clear` - Clear screen
- `echo` - Print text
- `ls` - List files
- `cd` - Change directory
- `pwd` - Print working directory
- `cat` - Display file contents
- `mkdir` - Create directory
- `rm` - Remove file
- `ps` - Show processes
- `kill` - Kill process
- `meminfo` - Memory information
- `neural_status` - Neural network status
- `train_model` - Train neural network

## Neural Features

NeuralOS includes advanced AI capabilities:

### Neural Networks
- Multi-layer perceptrons
- Backpropagation training
- Sigmoid, ReLU, Tanh, Softmax activations
- XOR example training included

### Federated Learning
- Distributed model training
- Model aggregation
- Node coordination

### Consensus
- Proof-of-learning validation
- Difficulty-based mining
- Decentralized decision making

## Development

### Adding New Features

1. **System Calls**: Add to `kernel/syscalls.cpp`
2. **Drivers**: Add to `arch/x86_64/`
3. **Commands**: Add to `kernel/shell.cpp`
4. **Neural Models**: Extend `kernel/neural_core.cpp`

### Testing

```bash
# Unit tests (when implemented)
make test

# Integration tests
make check
```

## Roadmap

- [ ] Complete filesystem implementation
- [ ] Network stack (TCP/IP)
- [ ] USB and PCI drivers
- [ ] User space and ELF loading
- [ ] Advanced neural architectures
- [ ] GUI subsystem
- [ ] Real-time capabilities

## Contributing

This is a complete operating system rewrite. Contributions welcome for:
- Device drivers
- File system improvements
- Neural network enhancements
- Documentation
- Testing

## License

MIT License - see LICENSE file for details.