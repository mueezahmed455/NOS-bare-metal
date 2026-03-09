#include "memory.h"
#include "kernel.h"
#include "console.h"

// Memory manager static members
page_directory_entry_t* MemoryManager::page_directory = nullptr;
u32* MemoryManager::page_frames = nullptr;
size_t MemoryManager::total_frames = 0;
size_t MemoryManager::used_frames = 0;

void MemoryManager::initialize() {
    // Calculate total memory (assume 128MB for now)
    total_frames = (128 * 1024 * 1024) / PAGE_SIZE;
    used_frames = 0;

    // Allocate page frame bitmap
    page_frames = static_cast<u32*>(kmalloc(total_frames / 32 * sizeof(u32)));
    memset(page_frames, 0, total_frames / 32 * sizeof(u32));

    // Allocate page directory
    page_directory = static_cast<page_directory_entry_t*>(kmalloc(PAGE_SIZE));
    memset(page_directory, 0, PAGE_SIZE);

    // Mark kernel memory as used (first 1MB)
    allocate_region(0, 1024 * 1024, true, false);

    klog(LogLevel::INFO, "Memory manager initialized: %d frames available", total_frames);
}

void* MemoryManager::allocate_page() {
    size_t frame = first_free_frame();
    if (frame == static_cast<size_t>(-1)) {
        return nullptr;
    }

    set_page_frame(frame, true);
    used_frames++;

    return reinterpret_cast<void*>(frame * PAGE_SIZE);
}

void MemoryManager::free_page(void* page) {
    uintptr_t frame = reinterpret_cast<uintptr_t>(page) / PAGE_SIZE;
    set_page_frame(frame, false);
    used_frames--;
}

void* MemoryManager::allocate_pages(size_t count) {
    // Find contiguous free frames
    size_t start_frame = static_cast<size_t>(-1);
    size_t consecutive = 0;

    for (size_t i = 0; i < total_frames; i++) {
        if (!get_page_frame(i)) {
            if (start_frame == static_cast<size_t>(-1)) {
                start_frame = i;
            }
            consecutive++;
            if (consecutive >= count) {
                break;
            }
        } else {
            start_frame = static_cast<size_t>(-1);
            consecutive = 0;
        }
    }

    if (consecutive < count) {
        return nullptr;
    }

    // Mark frames as used
    for (size_t i = 0; i < count; i++) {
        set_page_frame(start_frame + i, true);
    }
    used_frames += count;

    return reinterpret_cast<void*>(start_frame * PAGE_SIZE);
}

void MemoryManager::free_pages(void* pages, size_t count) {
    uintptr_t start_frame = reinterpret_cast<uintptr_t>(pages) / PAGE_SIZE;
    for (size_t i = 0; i < count; i++) {
        set_page_frame(start_frame + i, false);
    }
    used_frames -= count;
}

void MemoryManager::map_page(void* virtual_addr, void* physical_addr, bool writable, bool user) {
    uintptr_t vaddr = reinterpret_cast<uintptr_t>(virtual_addr);
    uintptr_t paddr = reinterpret_cast<uintptr_t>(physical_addr);

    // Calculate page directory and table indices
    u32 pd_index = vaddr >> 22;
    u32 pt_index = (vaddr >> 12) & 0x3FF;

    // Check if page table exists
    if (!(page_directory[pd_index] & 1)) {
        // Allocate page table
        void* pt = allocate_page();
        if (!pt) {
            panic("Failed to allocate page table");
        }

        page_directory[pd_index] = reinterpret_cast<uintptr_t>(pt) | 3; // Present, writable, supervisor
        memset(pt, 0, PAGE_SIZE);
    }

    // Get page table
    u32* page_table = reinterpret_cast<u32*>(page_directory[pd_index] & ~0xFFF);

    // Map the page
    u32 flags = 1; // Present
    if (writable) flags |= 2;
    if (user) flags |= 4;

    page_table[pt_index] = (paddr & ~0xFFF) | flags;
}

void MemoryManager::unmap_page(void* virtual_addr) {
    uintptr_t vaddr = reinterpret_cast<uintptr_t>(virtual_addr);
    u32 pd_index = vaddr >> 22;
    u32 pt_index = (vaddr >> 12) & 0x3FF;

    if (page_directory[pd_index] & 1) {
        u32* page_table = reinterpret_cast<u32*>(page_directory[pd_index] & ~0xFFF);
        page_table[pt_index] = 0;
    }
}

void* MemoryManager::get_physical_address(void* virtual_addr) {
    uintptr_t vaddr = reinterpret_cast<uintptr_t>(virtual_addr);
    u32 pd_index = vaddr >> 22;
    u32 pt_index = (vaddr >> 12) & 0x3FF;

    if (!(page_directory[pd_index] & 1)) {
        return nullptr;
    }

    u32* page_table = reinterpret_cast<u32*>(page_directory[pd_index] & ~0xFFF);
    u32 entry = page_table[pt_index];

    if (!(entry & 1)) {
        return nullptr;
    }

    return reinterpret_cast<void*>((entry & ~0xFFF) + (vaddr & 0xFFF));
}

void MemoryManager::set_page_frame(size_t frame, bool used) {
    u32 index = frame / 32;
    u32 bit = frame % 32;

    if (used) {
        page_frames[index] |= (1 << bit);
    } else {
        page_frames[index] &= ~(1 << bit);
    }
}

bool MemoryManager::get_page_frame(size_t frame) {
    u32 index = frame / 32;
    u32 bit = frame % 32;
    return (page_frames[index] & (1 << bit)) != 0;
}

size_t MemoryManager::first_free_frame() {
    for (size_t i = 0; i < total_frames; i++) {
        if (!get_page_frame(i)) {
            return i;
        }
    }
    return static_cast<size_t>(-1);
}

void MemoryManager::allocate_region(uintptr_t start, uintptr_t end, bool writable, bool user) {
    uintptr_t start_frame = start / PAGE_SIZE;
    uintptr_t end_frame = end / PAGE_SIZE;

    for (u32 frame = start_frame; frame < end_frame; frame++) {
        set_page_frame(frame, true);
        used_frames++;
    }
}

// Heap allocator static members
HeapAllocator::Block* HeapAllocator::heap_start = nullptr;
size_t HeapAllocator::heap_size = 0;

void HeapAllocator::initialize() {
    heap_start = static_cast<Block*>(kmalloc(KERNEL_HEAP_SIZE));
    heap_size = KERNEL_HEAP_SIZE;

    heap_start->size = heap_size - sizeof(Block);
    heap_start->free = true;
    heap_start->next = nullptr;

    klog(LogLevel::INFO, "Heap allocator initialized: %d bytes", heap_size);
}

void* HeapAllocator::allocate(size_t size) {
    if (size == 0) return nullptr;

    // Align size to 8 bytes
    size = (size + 7) & ~7;

    Block* current = heap_start;
    while (current) {
        if (current->free && current->size >= size) {
            // Split block if too large
            if (current->size >= size + sizeof(Block) + 8) {
                Block* new_block = reinterpret_cast<Block*>(
                    reinterpret_cast<char*>(current) + sizeof(Block) + size);
                new_block->size = current->size - size - sizeof(Block);
                new_block->free = true;
                new_block->next = current->next;

                current->size = size;
                current->next = new_block;
            }

            current->free = false;
            return reinterpret_cast<char*>(current) + sizeof(Block);
        }
        current = current->next;
    }

    return nullptr; // No suitable block found
}

void HeapAllocator::deallocate(void* ptr) {
    if (!ptr) return;

    Block* block = reinterpret_cast<Block*>(reinterpret_cast<char*>(ptr) - sizeof(Block));
    block->free = true;

    // Merge with next block if free
    if (block->next && block->next->free) {
        block->size += sizeof(Block) + block->next->size;
        block->next = block->next->next;
    }

    // Merge with previous block if free (traverse from start)
    Block* current = heap_start;
    while (current && current->next != block) {
        current = current->next;
    }

    if (current && current->free && block->free) {
        current->size += sizeof(Block) + block->size;
        current->next = block->next;
    }
}

void* HeapAllocator::reallocate(void* ptr, size_t size) {
    if (!ptr) return allocate(size);
    if (size == 0) {
        deallocate(ptr);
        return nullptr;
    }

    Block* block = reinterpret_cast<Block*>(reinterpret_cast<char*>(ptr) - sizeof(Block));

    if (block->size >= size) {
        return ptr; // Current block is large enough
    }

    // Allocate new block and copy data
    void* new_ptr = allocate(size);
    if (new_ptr) {
        memcpy(new_ptr, ptr, block->size);
        deallocate(ptr);
    }
    return new_ptr;
}