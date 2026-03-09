#ifndef MEMORY_H
#define MEMORY_H

#include "kernel.h"

// Simple heap-based memory allocator
#define HEAP_SIZE (1024 * 1024)  // 1MB heap
#define HEAP_START 0x1000000     // Start at 16MB

struct MemoryBlock {
    size_t size;
    bool free;
    MemoryBlock* next;
};

class Memory {
public:
    static void initialize();
    static void* allocate(size_t size);
    static void deallocate(void* ptr);
    static size_t getTotalMemory();
    static size_t getUsedMemory();

private:
    static u8* heap_start;
    static size_t heap_size;
    static MemoryBlock* first_block;
    static size_t used_memory;
};

// C-compatible allocation functions
void* kmalloc(size_t size);
void kfree(void* ptr);
void memset(void* dest, u8 value, size_t count);
void memcpy(void* dest, const void* src, size_t count);
int memcmp(const void* s1, const void* s2, size_t n);

#endif // MEMORY_H
