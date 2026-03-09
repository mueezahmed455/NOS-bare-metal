#include "kernel.h"
#include "console.h"
#include "memory.h"
#include "scheduler.h"
#include "neural_core.h"
#include "filesystem.h"
#include "shell.h"
#include "../arch/x86_64/arch.h"

// Kernel main entry point
extern "C" void kernel_main() {
    // Initialize architecture-specific features
    Arch::initialize();

    // Initialize console for output
    Console::initialize();
    Console::clear();
    Console::puts("NeuralOS v" KERNEL_VERSION " - Booting...\n");

    // Initialize memory management
    klog(LogLevel::INFO, "Initializing memory management...");
    MemoryManager::initialize();
    HeapAllocator::initialize();

    // Initialize scheduler
    klog(LogLevel::INFO, "Initializing process scheduler...");
    Scheduler::initialize();

    // Initialize neural core
    klog(LogLevel::INFO, "Initializing neural processing core...");
    NeuralCore::initialize();
    FederatedCoordinator::initialize();
    ConsensusEngine::initialize();

    // Initialize file system
    klog(LogLevel::INFO, "Initializing file system...");
    FileSystem::initialize();

    // Initialize shell
    klog(LogLevel::INFO, "Initializing command shell...");
    Shell::initialize();

    klog(LogLevel::INFO, "NeuralOS kernel initialized successfully!");
    Console::puts("Welcome to NeuralOS!\n");
    Console::puts("Type 'help' for available commands.\n\n");

    // Start the shell
    Shell::run();

    // If shell exits, halt the system
    klog(LogLevel::INFO, "Shell exited, halting system...");
    Arch::halt();
}