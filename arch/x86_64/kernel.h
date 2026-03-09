#ifndef KERNEL_H
#define KERNEL_H

#include <cstdint>
#include <cstddef>

// Basic types
using u8 = uint8_t;
using u16 = uint16_t;
using u32 = uint32_t;
using u64 = uint64_t;
using i8 = int8_t;
using i16 = int16_t;
using i32 = int32_t;
using i64 = int64_t;
using usize = size_t;

// Log levels
enum class LogLevel {
    DEBUG,
    INFO,
    WARNING,
    ERROR
};

// Kernel logging function
void klog(LogLevel level, const char* message);

// Memory functions
void* kmalloc(size_t size);
void kfree(void* ptr);
void memset(void* dest, u8 value, size_t count);
void memcpy(void* dest, const void* src, size_t count);
int memcmp(const void* s1, const void* s2, size_t n);

// Page table types for x86_64
using page_entry_t = u64;
using page_table_t = page_entry_t[512];
using page_directory_t = page_table_t[512];

// Multiboot2 structures
struct multiboot_info {
    u32 flags;
    u32 mem_lower;
    u32 mem_upper;
    u32 boot_device;
    u32 cmdline;
    u32 mods_count;
    u32 mods_addr;
    u32 syms[4];
    u32 mmap_length;
    u32 mmap_addr;
    u32 drives_length;
    u32 drives_addr;
    u32 config_table;
    u32 boot_loader_name;
    u32 apm_table;
    u32 vbe_mode_info;
    u32 vbe_mode;
    u32 vbe_interface_seg;
    u32 vbe_interface_off;
    u32 vbe_interface_len;
    u32 framebuffer_addr;
    u32 framebuffer_pitch;
    u32 framebuffer_width;
    u32 framebuffer_height;
    u8 framebuffer_bpp;
    u8 framebuffer_type;
    u16 reserved;
    u32 framebuffer_red_mask;
    u32 framebuffer_green_mask;
    u32 framebuffer_blue_mask;
};

// Kernel main entry point
extern "C" void kernel_main();

#endif // KERNEL_H
