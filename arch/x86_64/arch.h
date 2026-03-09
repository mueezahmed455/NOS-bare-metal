#ifndef ARCH_X86_64_H
#define ARCH_X86_64_H

#include <cstdint>

// Basic type definitions (duplicate from kernel.h to avoid circular dependency)
using u8 = uint8_t;
using u16 = uint16_t;
using u32 = uint32_t;
using u64 = uint64_t;

// x86_64 specific constants
#define KERNEL_VIRTUAL_BASE 0xFFFFFFFF80000000
#define PAGE_SIZE_4KB 4096
#define PAGE_SIZE_2MB (2 * 1024 * 1024)
#define PAGE_SIZE_1GB (1024 * 1024 * 1024)

// CPU structures
struct GDTEntry {
    u16 limit_low;
    u16 base_low;
    u8 base_middle;
    u8 access;
    u8 granularity;
    u8 base_high;
} __attribute__((packed));

struct GDTPointer {
    u16 limit;
    u64 base;
} __attribute__((packed));

struct IDTEntry {
    u16 offset_low;
    u16 selector;
    u8 ist;
    u8 type_attr;
    u16 offset_middle;
    u32 offset_high;
    u32 zero;
} __attribute__((packed));

struct IDTPointer {
    u16 limit;
    u64 base;
} __attribute__((packed));

// Architecture class
class Arch {
public:
    static void initialize();
    static void halt();
    static void enable_interrupts();
    static void disable_interrupts();
    static void set_interrupt_handler(u8 vector, void (*handler)());
    static void outb(u16 port, u8 value);
    static u8 inb(u16 port);
    static void outw(u16 port, u16 value);
    static u16 inw(u16 port);
    static void outl(u16 port, u32 value);
    static u32 inl(u16 port);

private:
    static GDTEntry gdt[5];
    static GDTPointer gdt_ptr;
    static IDTEntry idt[256];
    static IDTPointer idt_ptr;

    static void setup_gdt();
    static void setup_idt();
    static void setup_paging();
};

#endif // ARCH_X86_64_H