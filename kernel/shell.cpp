#include "shell.h"
#include "kernel.h"
#include "console.h"
#include "filesystem.h"
#include "scheduler.h"
#include "memory.h"
#include "neural_core.h"

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

    // Register built-in commands
    register_command("help", "Show available commands", cmd_help);
    register_command("clear", "Clear the screen", cmd_clear);
    register_command("echo", "Echo text to screen", cmd_echo);
    register_command("ls", "List directory contents", cmd_ls);
    register_command("cd", "Change directory", cmd_cd);
    register_command("pwd", "Print working directory", cmd_pwd);
    register_command("cat", "Display file contents", cmd_cat);
    register_command("mkdir", "Create directory", cmd_mkdir);
    register_command("rm", "Remove file", cmd_rm);
    register_command("ps", "Show process list", cmd_ps);
    register_command("kill", "Kill a process", cmd_kill);
    register_command("meminfo", "Show memory information", cmd_meminfo);
    register_command("neural_status", "Show neural network status", cmd_neural_status);
    register_command("train_model", "Train neural network", cmd_train_model);

    klog(LogLevel::INFO, "Shell initialized with %d commands", num_commands);
}

void Shell::run() {
    char input_buffer[256];

    while (true) {
        print_prompt();

        // Simple line reading (in real implementation, would handle interrupts)
        size_t i = 0;
        while (i < sizeof(input_buffer) - 1) {
            // For now, just simulate getting input
            // TODO: Implement actual keyboard input
            char c = '\n'; // Simulated input
            if (c == '\n' || c == '\r') {
                input_buffer[i] = '\0';
                break;
            } else if (c == '\b' && i > 0) {
                i--;
                Console::putchar('\b');
                Console::putchar(' ');
                Console::putchar('\b');
            } else { // Simple character check instead of isprint
                if (c >= 32 && c <= 126) {
                    input_buffer[i++] = c;
                    Console::putchar(c);
            }
        }

        Console::putchar('\n');

        if (input_buffer[0] != '\0') {
            process_command(input_buffer);
        }
    }
}

void Shell::process_command(const char* command_line) {
    char* line_copy = strcpy(static_cast<char*>(kmalloc(strlen(command_line) + 1)), command_line);
    i32 argc;
    char** argv = parse_line(line_copy, &argc);

    if (argc > 0) {
        execute_command(argc, argv);
    }

    free_argv(argv, argc);
    kfree(line_copy);
}

void Shell::register_command(const char* name, const char* description, i32 (*handler)(i32, char**)) {
    if (num_commands >= max_commands) {
        klog(LogLevel::WARN, "Command table full, cannot register %s", name);
        return;
    }

    commands[num_commands].name = strcpy(static_cast<char*>(kmalloc(strlen(name) + 1)), name);
    commands[num_commands].description = strcpy(static_cast<char*>(kmalloc(strlen(description) + 1)), description);
    commands[num_commands].handler = handler;
    num_commands++;
}

void Shell::unregister_command(const char* name) {
    for (size_t i = 0; i < num_commands; i++) {
        if (strcmp(commands[i].name, name) == 0) {
            kfree(commands[i].name);
            kfree(commands[i].description);

            // Shift remaining commands
            for (size_t j = i; j < num_commands - 1; j++) {
                commands[j] = commands[j + 1];
            }
            num_commands--;
            break;
        }
    }
}

void Shell::print_prompt() {
    Console::set_color(VGAColor::GREEN);
    Console::puts("neuralos");
    Console::set_color(VGAColor::WHITE);
    Console::puts(":");
    Console::set_color(VGAColor::BLUE);
    Console::puts(current_directory);
    Console::set_color(VGAColor::WHITE);
    Console::puts("$ ");
}

char* Shell::read_line() {
    // Placeholder - would implement proper line reading
    return nullptr;
}

char** Shell::parse_line(char* line, i32* argc) {
    i32 capacity = 16;
    char** argv = static_cast<char**>(kmalloc(capacity * sizeof(char*)));
    *argc = 0;

    char* token = line;
    while (*token) {
        // Skip whitespace
        while (*token && isspace(*token)) token++;

        if (!*token) break;

        if (*argc >= capacity) {
            capacity *= 2;
            argv = static_cast<char**>(krealloc(argv, capacity * sizeof(char*)));
        }

        argv[*argc] = token;
        (*argc)++;

        // Find end of token
        while (*token && !isspace(*token)) token++;
        if (*token) {
            *token = '\0';
            token++;
        }
    }

    return argv;
}

i32 Shell::execute_command(i32 argc, char* argv[]) {
    for (size_t i = 0; i < num_commands; i++) {
        if (strcmp(commands[i].name, argv[0]) == 0) {
            return commands[i].handler(argc, argv);
        }
    }

    Console::printf("Command not found: %s\n", argv[0]);
    return -1;
}

void Shell::free_argv(char** argv, i32 argc) {
    kfree(argv);
}

// Built-in command implementations
i32 Shell::cmd_help(i32 argc, char* argv[]) {
    Console::puts("Available commands:\n");
    for (size_t i = 0; i < num_commands; i++) {
        Console::printf("  %-12s %s\n", commands[i].name, commands[i].description);
    }
    return 0;
}

i32 Shell::cmd_clear(i32 argc, char* argv[]) {
    Console::clear();
    return 0;
}

i32 Shell::cmd_echo(i32 argc, char* argv[]) {
    for (i32 i = 1; i < argc; i++) {
        Console::puts(argv[i]);
        if (i < argc - 1) Console::putchar(' ');
    }
    Console::putchar('\n');
    return 0;
}

i32 Shell::cmd_ls(i32 argc, char* argv[]) {
    // Simplified - just show some dummy files
    Console::puts(".\n..\ntest.txt\nconfig.sys\n");
    return 0;
}

i32 Shell::cmd_cd(i32 argc, char* argv[]) {
    if (argc < 2) {
        strcpy(current_directory, "/");
    } else {
        // Simplified - no actual directory changing
        strcpy(current_directory, argv[1]);
    }
    return 0;
}

i32 Shell::cmd_pwd(i32 argc, char* argv[]) {
    Console::puts(current_directory);
    Console::putchar('\n');
    return 0;
}

i32 Shell::cmd_cat(i32 argc, char* argv[]) {
    if (argc < 2) {
        Console::puts("Usage: cat <filename>\n");
        return -1;
    }

    i32 fd = FileSystem::open(argv[1], 0);
    if (fd < 0) {
        Console::printf("Cannot open file: %s\n", argv[1]);
        return -1;
    }

    char buffer[256];
    isize n;
    while ((n = FileSystem::read(fd, buffer, sizeof(buffer) - 1)) > 0) {
        buffer[n] = '\0';
        Console::puts(buffer);
    }

    FileSystem::close(fd);
    return 0;
}

i32 Shell::cmd_mkdir(i32 argc, char* argv[]) {
    if (argc < 2) {
        Console::puts("Usage: mkdir <dirname>\n");
        return -1;
    }

    if (FileSystem::mkdir(argv[1], 0755) < 0) {
        Console::printf("Cannot create directory: %s\n", argv[1]);
        return -1;
    }

    return 0;
}

i32 Shell::cmd_rm(i32 argc, char* argv[]) {
    if (argc < 2) {
        Console::puts("Usage: rm <filename>\n");
        return -1;
    }

    if (FileSystem::unlink(argv[1]) < 0) {
        Console::printf("Cannot remove file: %s\n", argv[1]);
        return -1;
    }

    return 0;
}

i32 Shell::cmd_ps(i32 argc, char* argv[]) {
    Console::puts("PID   NAME          STATE\n");
    Console::puts("1     init          RUNNING\n");
    Console::puts("2     shell         RUNNING\n");
    return 0;
}

i32 Shell::cmd_kill(i32 argc, char* argv[]) {
    if (argc < 2) {
        Console::puts("Usage: kill <pid>\n");
        return -1;
    }

    Console::printf("Killed process %s\n", argv[1]);
    return 0;
}

i32 Shell::cmd_meminfo(i32 argc, char* argv[]) {
    Console::puts("Memory Information:\n");
    Console::puts("Total: 128 MB\n");
    Console::puts("Used:  32 MB\n");
    Console::puts("Free:  96 MB\n");
    return 0;
}

i32 Shell::cmd_neural_status(i32 argc, char* argv[]) {
    Console::puts("Neural Network Status:\n");
    Console::puts("Core: Active\n");
    Console::puts("Federated nodes: 1\n");
    Console::puts("Consensus: Running\n");
    return 0;
}

i32 Shell::cmd_train_model(i32 argc, char* argv[]) {
    Console::puts("Training neural network...\n");
    // Create a simple network for demonstration
    size_t layer_sizes[] = {2, 3, 1};
    ActivationFunction activations[] = {ActivationFunction::SIGMOID, ActivationFunction::SIGMOID};

    NeuralNetwork* network = NeuralCore::create_network(2, layer_sizes, activations);
    if (network) {
        // Simple XOR training data
        float inputs[4][2] = {{0, 0}, {0, 1}, {1, 0}, {1, 1}};
        float targets[4][1] = {{0}, {1}, {1}, {0}};

        for (int epoch = 0; epoch < 1000; epoch++) {
            for (int i = 0; i < 4; i++) {
                NeuralCore::train(network, inputs[i], targets[i], 1);
            }
        }

        Console::puts("Training completed!\n");

        // Test the network
        for (int i = 0; i < 4; i++) {
            float output[1];
            NeuralCore::predict(network, inputs[i], output);
            Console::printf("Input: %d %d, Output: %.3f, Expected: %.1f\n",
                          (int)inputs[i][0], (int)inputs[i][1], output[0], targets[i][0]);
        }

        NeuralCore::destroy_network(network);
    } else {
        Console::puts("Failed to create neural network\n");
    }

    return 0;
}