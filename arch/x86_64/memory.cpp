#include "memory.h"
#include "console.h"

u8* Memory::heap_start = nullptr;
size_t Memory::heap_size = HEAP_SIZE;
MemoryBlock* Memory::first_block = nullptr;
size_t Memory::used_memory = 0;

void Memory::initialize() {
    heap_start = reinterpret_cast<u8*>(HEAP_START);
    heap_size = HEAP_SIZE;
    used_memory = 0;
    
    // Initialize the first block to span the entire heap
    first_block = reinterpret_cast<MemoryBlock*>(heap_start);
    first_block->size = heap_size - sizeof(MemoryBlock);
    first_block->free = true;
    first_block->next = nullptr;
}

void* Memory::allocate(size_t size) {
    if (size == 0) {
        return nullptr;
    }
    
    // Align size to 8 bytes
    size = (size + 7) & ~7;
    
    MemoryBlock* current = first_block;
    
    while (current != nullptr) {
        if (current->free && current->size >= size) {
            // Found a suitable block
            size_t remaining = current->size - size - sizeof(MemoryBlock);
            
            // Split the block if there's enough space for another block
            if (remaining > sizeof(MemoryBlock) + 8) {
                MemoryBlock* new_block = reinterpret_cast<MemoryBlock*>(
                    reinterpret_cast<u8*>(current) + sizeof(MemoryBlock) + size
                );
                new_block->size = remaining - sizeof(MemoryBlock);
                new_block->free = true;
                new_block->next = current->next;
                current->next = new_block;
                current->size = size;
            }
            
            current->free = false;
            used_memory += current->size;
            
            return reinterpret_cast<u8*>(current) + sizeof(MemoryBlock);
        }
        current = current->next;
    }
    
    // No suitable block found
    return nullptr;
}

void Memory::deallocate(void* ptr) {
    if (ptr == nullptr) {
        return;
    }
    
    MemoryBlock* block = reinterpret_cast<MemoryBlock*>(
        reinterpret_cast<u8*>(ptr) - sizeof(MemoryBlock)
    );
    
    used_memory -= block->size;
    block->free = true;
    
    // Coalesce adjacent free blocks
    MemoryBlock* current = first_block;
    while (current != nullptr && current->next != nullptr) {
        if (current->free && current->next->free) {
            current->size += sizeof(MemoryBlock) + current->next->size;
            current->next = current->next->next;
        } else {
            current = current->next;
        }
    }
}

size_t Memory::getTotalMemory() {
    return heap_size;
}

size_t Memory::getUsedMemory() {
    return used_memory;
}

// C-compatible allocation functions
void* kmalloc(size_t size) {
    return Memory::allocate(size);
}

void kfree(void* ptr) {
    Memory::deallocate(ptr);
}

void memset(void* dest, u8 value, size_t count) {
    u8* d = reinterpret_cast<u8*>(dest);
    for (size_t i = 0; i < count; i++) {
        d[i] = value;
    }
}

void memcpy(void* dest, const void* src, size_t count) {
    const u8* s = reinterpret_cast<const u8*>(src);
    u8* d = reinterpret_cast<u8*>(dest);
    for (size_t i = 0; i < count; i++) {
        d[i] = s[i];
    }
}

int memcmp(const void* s1, const void* s2, size_t n) {
    const u8* p1 = reinterpret_cast<const u8*>(s1);
    const u8* p2 = reinterpret_cast<const u8*>(s2);
    
    for (size_t i = 0; i < n; i++) {
        if (p1[i] != p2[i]) {
            return p1[i] - p2[i];
        }
    }
    return 0;
}
