#ifndef MEMORY_H
#define MEMORY_H

#include <cstdint>
#include <cstddef>
#include "kernel.h"

// Memory management constants
#define PAGE_SIZE 4096
#define KERNEL_HEAP_START 0x100000
#define KERNEL_HEAP_SIZE (16 * 1024 * 1024) // 16MB

// Page frame structure
struct PageFrame {
    bool present : 1;
    bool writable : 1;
    bool user : 1;
    bool write_through : 1;
    bool cache_disabled : 1;
    bool accessed : 1;
    bool dirty : 1;
    bool page_size : 1;
    bool global : 1;
    u8 available : 3;
    u32 frame : 20;
} __attribute__((packed));

// Page directory entry
using page_directory_entry_t = u32;

// Memory manager class
class MemoryManager {
public:
    static void initialize();
    static void* allocate_page();
    static void free_page(void* page);
    static void* allocate_pages(size_t count);
    static void free_pages(void* pages, size_t count);
    static void map_page(void* virtual_addr, void* physical_addr, bool writable = true, bool user = false);
    static void unmap_page(void* virtual_addr);
    static void* get_physical_address(void* virtual_addr);

private:
    static page_directory_entry_t* page_directory;
    static u32* page_frames;
    static size_t total_frames;
    static size_t used_frames;

    static void set_page_frame(size_t frame, bool used);
    static bool get_page_frame(size_t frame);
    static size_t first_free_frame();
    static void allocate_region(uintptr_t start, uintptr_t end, bool writable, bool user);
};

// Heap allocator
class HeapAllocator {
public:
    static void initialize();
    static void* allocate(size_t size);
    static void deallocate(void* ptr);
    static void* reallocate(void* ptr, size_t size);

private:
    struct Block {
        size_t size;
        bool free;
        Block* next;
    };

    static Block* heap_start;
    static size_t heap_size;
};

#endif // MEMORY_H