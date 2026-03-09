#include "arch.h"
#include "kernel.h"
#include "memory.h"
#include "console.h"

// GDT and IDT static members
GDTEntry Arch::gdt[5];
GDTPointer Arch::gdt_ptr;
IDTEntry Arch::idt[256];
IDTPointer Arch::idt_ptr;

// External assembly functions
extern "C" {
    void load_gdt(u64 gdt_ptr);
    void load_idt(u64 idt_ptr);
    void timer_interrupt();
    void generic_interrupt();
    void divide_by_zero();
    void page_fault();
}

void Arch::initialize() {
    setup_gdt();
    setup_idt();
    setup_paging();

    klog(LogLevel::INFO, "x86_64 architecture initialized");
}

void Arch::halt() {
    asm volatile("hlt");
}

void Arch::enable_interrupts() {
    asm volatile("sti");
}

void Arch::disable_interrupts() {
    asm volatile("cli");
}

void Arch::set_interrupt_handler(u8 vector, void (*handler)()) {
    idt[vector].offset_low = (u16)((u64)handler & 0xFFFF);
    idt[vector].offset_middle = (u16)(((u64)handler >> 16) & 0xFFFF);
    idt[vector].offset_high = (u32)(((u64)handler >> 32) & 0xFFFFFFFF);
    idt[vector].type_attr = 0x8E; // Interrupt gate, present, DPL 0
    idt[vector].selector = 0x08; // Code segment
    idt[vector].ist = 0;
    idt[vector].zero = 0;
}

void Arch::outb(u16 port, u8 value) {
    asm volatile("outb %0, %1" : : "a"(value), "Nd"(port));
}

u8 Arch::inb(u16 port) {
    u8 value;
    asm volatile("inb %1, %0" : "=a"(value) : "Nd"(port));
    return value;
}

void Arch::outw(u16 port, u16 value) {
    asm volatile("outw %0, %1" : : "a"(value), "Nd"(port));
}

u16 Arch::inw(u16 port) {
    u16 value;
    asm volatile("inw %1, %0" : "=a"(value) : "Nd"(port));
    return value;
}

void Arch::outl(u16 port, u32 value) {
    asm volatile("outl %0, %1" : : "a"(value), "Nd"(port));
}

u32 Arch::inl(u16 port) {
    u32 value;
    asm volatile("inl %1, %0" : "=a"(value) : "Nd"(port));
    return value;
}

void Arch::setup_gdt() {
    // Null descriptor (required, must be first)
    gdt[0] = {0, 0, 0, 0, 0, 0};

    // Code segment (kernel, ring 0)
    // Base: 0, Limit: 0xFFFFFFFF, Type: Execute/Read, DPL: 0, Present, Long mode
    gdt[1].limit_low = 0xFFFF;
    gdt[1].base_low = 0x0000;
    gdt[1].base_middle = 0x00;
    gdt[1].access = 0x9A; // Present, DPL 0, Code, Executable, Accessed
    gdt[1].granularity = 0xAF; // 4KB pages, 64-bit mode
    gdt[1].base_high = 0x00;

    // Data segment (kernel, ring 0)
    // Base: 0, Limit: 0xFFFFFFFF, Type: Read/Write, DPL: 0, Present
    gdt[2].limit_low = 0xFFFF;
    gdt[2].base_low = 0x0000;
    gdt[2].base_middle = 0x00;
    gdt[2].access = 0x92; // Present, DPL 0, Data, Writable, Accessed
    gdt[2].granularity = 0xCF; // 4KB pages
    gdt[2].base_high = 0x00;

    // Code segment (user, ring 3)
    gdt[3].limit_low = 0xFFFF;
    gdt[3].base_low = 0x0000;
    gdt[3].base_middle = 0x00;
    gdt[3].access = 0xFA; // Present, DPL 3, Code, Executable, Accessed
    gdt[3].granularity = 0xAF; // 4KB pages, 64-bit mode
    gdt[3].base_high = 0x00;

    // Data segment (user, ring 3)
    gdt[4].limit_low = 0xFFFF;
    gdt[4].base_low = 0x0000;
    gdt[4].base_middle = 0x00;
    gdt[4].access = 0xF2; // Present, DPL 3, Data, Writable, Accessed
    gdt[4].granularity = 0xCF; // 4KB pages
    gdt[4].base_high = 0x00;

    gdt_ptr.limit = sizeof(gdt) - 1;
    gdt_ptr.base = (u64)&gdt;

    // Load GDT
    asm volatile(
        "lgdt %0"
        :
        : "m"(gdt_ptr)
        : "memory"
    );

    // Reload segment registers
    asm volatile(
        "push 0x10\n"
        "lea 1f(%%rip), %%rax\n"
        "push %%rax\n"
        "retfq\n"
        "1:\n"
        "mov $0x10, %%ax\n"
        "mov %%ax, %%ds\n"
        "mov %%ax, %%es\n"
        "mov %%ax, %%fs\n"
        "mov %%ax, %%gs\n"
        "mov %%ax, %%ss\n"
        :
        :
        : "rax", "memory"
    );

    klog(LogLevel::INFO, "GDT initialized");
}

void Arch::setup_idt() {
    idt_ptr.limit = sizeof(idt) - 1;
    idt_ptr.base = (u64)&idt;

    // Initialize all IDT entries to 0
    memset(idt, 0, sizeof(idt));

    // Set up exception handlers (vectors 0-31)
    set_interrupt_handler(0, (void(*)())divide_by_zero);
    set_interrupt_handler(1, (void(*)())generic_interrupt);
    set_interrupt_handler(2, (void(*)())generic_interrupt);
    set_interrupt_handler(3, (void(*)())generic_interrupt);
    set_interrupt_handler(4, (void(*)())generic_interrupt);
    set_interrupt_handler(5, (void(*)())generic_interrupt);
    set_interrupt_handler(6, (void(*)())generic_interrupt);
    set_interrupt_handler(7, (void(*)())generic_interrupt);
    set_interrupt_handler(8, (void(*)())generic_interrupt);
    set_interrupt_handler(10, (void(*)())generic_interrupt);
    set_interrupt_handler(11, (void(*)())generic_interrupt);
    set_interrupt_handler(12, (void(*)())generic_interrupt);
    set_interrupt_handler(13, (void(*)())generic_interrupt);
    set_interrupt_handler(14, (void(*)())page_fault);
    set_interrupt_handler(16, (void(*)())generic_interrupt);
    set_interrupt_handler(17, (void(*)())generic_interrupt);
    set_interrupt_handler(18, (void(*)())generic_interrupt);

    // Set up timer interrupt (IRQ 0, vector 32)
    set_interrupt_handler(32, (void(*)())timer_interrupt);

    // Load IDT
    asm volatile(
        "lidt %0"
        :
        : "m"(idt_ptr)
        : "memory"
    );

    klog(LogLevel::INFO, "IDT initialized");
}

void Arch::setup_paging() {
    // For now, we keep identity mapping or rely on bootloader paging
    // A full implementation would set up a proper 4-level page table
    
    // Enable Write Protect bit handling
    u64 cr0;
    asm volatile("mov %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x10000; // Set WP bit
    asm volatile("mov %0, %%cr0" : : "r"(cr0));

    klog(LogLevel::INFO, "Paging configured");
}
