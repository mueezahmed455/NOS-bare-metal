#include "scheduler.h"
#include "kernel.h"
#include "memory.h"
#include "arch.h"

// Scheduler static members
Process* Scheduler::current_process = nullptr;
Process* Scheduler::process_list = nullptr;
u32 Scheduler::next_pid = 1;

void Scheduler::initialize() {
    // Create idle process
    Process* idle = create_process("idle", []() {
        while (true) {
            Arch::halt();
        }
    }, 0);

    current_process = idle;
    klog(LogLevel::INFO, "Scheduler initialized with idle process");
}

Process* Scheduler::create_process(const char* name, void (*entry_point)(), u32 priority) {
    Process* process = static_cast<Process*>(kmalloc(sizeof(Process)));
    if (!process) {
        return nullptr;
    }

    // Allocate stack
    void* stack = MemoryManager::allocate_page();
    if (!stack) {
        kfree(process);
        return nullptr;
    }

    process->pid = next_pid++;
    process->state = ProcessState::READY;
    process->stack_top = reinterpret_cast<char*>(stack) + PAGE_SIZE;
    process->stack_bottom = stack;
    process->instruction_pointer = reinterpret_cast<void*>(entry_point);
    process->priority = priority;
    process->runtime = 0;
    process->next = nullptr;
    strcpy(process->name, name);

    // Add to process list
    if (!process_list) {
        process_list = process;
    } else {
        Process* current = process_list;
        while (current->next) {
            current = current->next;
        }
        current->next = process;
    }

    klog(LogLevel::INFO, "Created process %s (PID: %d)", name, process->pid);
    return process;
}

void Scheduler::terminate_process(Process* process) {
    if (!process) return;

    process->state = ProcessState::TERMINATED;

    // Free stack
    MemoryManager::free_page(process->stack_bottom);

    // Remove from process list
    if (process_list == process) {
        process_list = process->next;
    } else {
        Process* current = process_list;
        while (current && current->next != process) {
            current = current->next;
        }
        if (current) {
            current->next = process->next;
        }
    }

    kfree(process);
    klog(LogLevel::INFO, "Terminated process (PID: %d)", process->pid);
}

void Scheduler::schedule() {
    if (!process_list) return;

    Process* next_process = nullptr;
    Process* current = process_list;

    // Find next ready process
    while (current) {
        if (current != current_process && current->state == ProcessState::READY) {
            if (!next_process || current->priority > next_process->priority) {
                next_process = current;
            }
        }
        current = current->next;
    }

    if (next_process && next_process != current_process) {
        context_switch(current_process, next_process);
    }
}

void Scheduler::yield() {
    if (current_process) {
        current_process->state = ProcessState::READY;
    }
    schedule();
}

Process* Scheduler::get_current_process() {
    return current_process;
}

void Scheduler::block_current_process() {
    if (current_process) {
        current_process->state = ProcessState::BLOCKED;
        schedule();
    }
}

void Scheduler::unblock_process(Process* process) {
    if (process && process->state == ProcessState::BLOCKED) {
        process->state = ProcessState::READY;
    }
}

void Scheduler::context_switch(Process* old_process, Process* new_process) {
    if (old_process) {
        old_process->state = ProcessState::READY;
    }

    new_process->state = ProcessState::RUNNING;
    current_process = new_process;

    // Context switch would happen here with assembly
    // For now, just update current process
}

// Timer static members
volatile u64 Timer::ticks = 0;

void Timer::initialize(u32 frequency) {
    // Set up PIT (Programmable Interval Timer)
    u32 divisor = 1193180 / frequency;

    Arch::outb(0x43, 0x36); // Command byte
    Arch::outb(0x40, static_cast<u8>(divisor & 0xFF));
    Arch::outb(0x40, static_cast<u8>((divisor >> 8) & 0xFF));

    klog(LogLevel::INFO, "Timer initialized at %d Hz", frequency);
}

void Timer::set_frequency(u32 frequency) {
    initialize(frequency);
}

u64 Timer::get_ticks() {
    return ticks;
}

void Timer::timer_callback() {
    ticks++;
    Scheduler::schedule();
}