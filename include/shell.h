#ifndef SHELL_H
#define SHELL_H

#include <cstdint>
#include <cstddef>
#include "kernel.h"
#include "filesystem.h"

// Command structure
struct Command {
    char* name;
    char* description;
    i32 (*handler)(i32 argc, char* argv[]);
};

// Shell class
class Shell {
public:
    static void initialize();
    static void run();
    static void process_command(const char* command_line);
    static void register_command(const char* name, const char* description, i32 (*handler)(i32, char**));
    static void unregister_command(const char* name);

private:
    static Command* commands;
    static size_t num_commands;
    static size_t max_commands;
    static char current_directory[MAX_PATH_LENGTH];

    static void print_prompt();
    static char* read_line();
    static char** parse_line(char* line, i32* argc);
    static i32 execute_command(i32 argc, char* argv[]);
    static void free_argv(char** argv, i32 argc);

    // Built-in commands
    static i32 cmd_help(i32 argc, char* argv[]);
    static i32 cmd_clear(i32 argc, char* argv[]);
    static i32 cmd_echo(i32 argc, char* argv[]);
    static i32 cmd_ls(i32 argc, char* argv[]);
    static i32 cmd_cd(i32 argc, char* argv[]);
    static i32 cmd_pwd(i32 argc, char* argv[]);
    static i32 cmd_cat(i32 argc, char* argv[]);
    static i32 cmd_mkdir(i32 argc, char* argv[]);
    static i32 cmd_rm(i32 argc, char* argv[]);
    static i32 cmd_ps(i32 argc, char* argv[]);
    static i32 cmd_kill(i32 argc, char* argv[]);
    static i32 cmd_meminfo(i32 argc, char* argv[]);
    static i32 cmd_neural_status(i32 argc, char* argv[]);
    static i32 cmd_train_model(i32 argc, char* argv[]);
};

#endif // SHELL_H