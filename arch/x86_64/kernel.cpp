#include "kernel.h"
#include "arch.h"
#include "console.h"
#include "memory.h"

// Kernel logging implementation
void klog(LogLevel level, const char* message) {
    const char* level_str;
    switch (level) {
        case LogLevel::DEBUG:
            level_str = "[DEBUG] ";
            break;
        case LogLevel::INFO:
            level_str = "[INFO]  ";
            break;
        case LogLevel::WARNING:
            level_str = "[WARN]  ";
            break;
        case LogLevel::ERROR:
            level_str = "[ERROR] ";
            break;
        default:
            level_str = "[????]  ";
            break;
    }
    
    Console::print(level_str);
    Console::print(message);
    Console::putChar('\n');
}

// Timer callback (called from interrupt handler)
extern "C" void timer_callback() {
    // Simple timer tick handler
    static u64 ticks = 0;
    ticks++;
    
    if (ticks % 100 == 0) {
        // Print something every 100 ticks
    }
}

// Main kernel entry point
extern "C" void kernel_main() {
    // Initialize console first for output
    Console::initialize();
    Console::print("========================================\n");
    Console::print("       NeuralOS Kernel\n");
    Console::print("========================================\n\n");
    
    // Initialize memory manager
    Memory::initialize();
    klog(LogLevel::INFO, "Memory manager initialized");
    
    // Initialize architecture-specific components
    Arch::initialize();
    
    klog(LogLevel::INFO, "Kernel initialization complete");
    Console::print("\n");
    Console::print("System ready. Press any key...\n");
    
    // Main kernel loop
    while (true) {
        Arch::halt();
    }
}
