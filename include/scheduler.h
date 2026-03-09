#ifndef SCHEDULER_H
#define SCHEDULER_H

#include <cstdint>
#include <cstddef>
#include "kernel.h"

// Process states
enum class ProcessState {
    READY,
    RUNNING,
    BLOCKED,
    TERMINATED
};

// Process structure
struct Process {
    u32 pid;
    ProcessState state;
    void* stack_top;
    void* stack_bottom;
    void* instruction_pointer;
    u32 priority;
    u64 runtime;
    Process* next;
    char name[32];
};

// CPU context for context switching
struct CPUContext {
    u32 edi, esi, ebp, esp, ebx, edx, ecx, eax;
    u32 eip, eflags;
} __attribute__((packed));

// Scheduler class
class Scheduler {
public:
    static void initialize();
    static Process* create_process(const char* name, void (*entry_point)(), u32 priority = 1);
    static void terminate_process(Process* process);
    static void schedule();
    static void yield();
    static Process* get_current_process();
    static void block_current_process();
    static void unblock_process(Process* process);

private:
    static Process* current_process;
    static Process* process_list;
    static u32 next_pid;

    static void context_switch(Process* old_process, Process* new_process);
    static void save_context(CPUContext* context);
    static void load_context(CPUContext* context);
};

// Timer for preemptive scheduling
class Timer {
public:
    static void initialize(u32 frequency);
    static void set_frequency(u32 frequency);
    static u64 get_ticks();

private:
    static volatile u64 ticks;
    static void timer_callback();
};

#endif // SCHEDULER_H