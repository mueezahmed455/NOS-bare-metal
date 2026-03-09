#include "shell.h"
#include "kernel.h"
#include "console.h"
#include "filesystem.h"

// Shell static members
Command* Shell::commands = nullptr;
size_t Shell::num_commands = 0;
size_t Shell::max_commands = 32;
char Shell::current_directory[MAX_PATH_LENGTH] = "/";

void Shell::initialize() {
    commands = static_cast<Command*>(kmalloc(max_commands * sizeof(Command)));
    if (!commands) {
        panic("Failed to allocate command table");
    }
    klog(LogLevel::INFO, "Shell initialized");
}

void Shell::run() {
    klog(LogLevel::INFO, "Shell running");
    Console::puts("NeuralOS Shell\n");
    Console::puts("Type 'help' for commands\n");
    
    // For now, just print prompt indefinitely
    while (true) {
        print_prompt();
        // TODO: Implement actual input handling
    }
}

void Shell::process_command(const char* command_line) {
    if (!command_line) return;
    klog(LogLevel::INFO, "Processing command: %s", command_line);
}

void Shell::register_command(const char* name, const char* description, i32 (*handler)(i32, char**)) {
    // Simplified implementation
    klog(LogLevel::INFO, "Registered command: %s", name);
}

void Shell::unregister_command(const char* name) {
    // Simplified implementation
}

void Shell::print_prompt() {
    Console::puts("> ");
}
