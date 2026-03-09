#include "kernel.h"
#include "console.h"
#include "memory.h"
#include "arch.h"
#include <cstdarg>

// Global kernel functions
void panic(const char* message) {
    Console::set_color(VGAColor::WHITE, VGAColor::RED);
    Console::puts("KERNEL PANIC: ");
    Console::puts(message);
    Console::puts("\n");

    // Disable interrupts and halt
    Arch::disable_interrupts();
    Arch::halt();
}

void* kmalloc(size_t size) {
    return HeapAllocator::allocate(size);
}

void kfree(void* ptr) {
    HeapAllocator::deallocate(ptr);
}

void* krealloc(void* ptr, size_t size) {
    return HeapAllocator::reallocate(ptr, size);
}

// String utilities
size_t strlen(const char* str) {
    size_t len = 0;
    while (str[len]) len++;
    return len;
}

char* strcpy(char* dest, const char* src) {
    char* d = dest;
    while ((*d++ = *src++));
    return dest;
}

int strcmp(const char* a, const char* b) {
    while (*a && *b && *a == *b) {
        a++;
        b++;
    }
    return *a - *b;
}

void* memset(void* dest, int value, size_t count) {
    unsigned char* d = static_cast<unsigned char*>(dest);
    for (size_t i = 0; i < count; i++) {
        d[i] = static_cast<unsigned char>(value);
    }
    return dest;
}

void* memcpy(void* dest, const void* src, size_t count) {
    unsigned char* d = static_cast<unsigned char*>(dest);
    const unsigned char* s = static_cast<const unsigned char*>(src);
    for (size_t i = 0; i < count; i++) {
        d[i] = s[i];
    }
    return dest;
}

// Kernel logging
void klog(LogLevel level, const char* format, ...) {
    const char* level_str;
    VGAColor color;

    switch (level) {
        case LogLevel::DEBUG:
            level_str = "[DEBUG]";
            color = VGAColor::CYAN;
            break;
        case LogLevel::INFO:
            level_str = "[INFO]";
            color = VGAColor::GREEN;
            break;
        case LogLevel::WARN:
            level_str = "[WARN]";
            color = VGAColor::LIGHT_BROWN;
            break;
        case LogLevel::ERROR:
            level_str = "[ERROR]";
            color = VGAColor::RED;
            break;
    }

    Console::set_color(color);
    Console::puts(level_str);
    Console::set_color(VGAColor::WHITE);
    Console::puts(" ");

    va_list args;
    va_start(args, format);
    // Simple printf implementation for kernel
    const char* ptr = format;
    while (*ptr) {
        if (*ptr == '%') {
            ptr++;
            if (*ptr == 's') {
                const char* str = va_arg(args, const char*);
                Console::puts(str);
            } else if (*ptr == 'd') {
                int num = va_arg(args, int);
                char buf[32];
                itoa(num, buf, 10);
                Console::puts(buf);
            } else if (*ptr == 'x') {
                unsigned int num = va_arg(args, unsigned int);
                char buf[32];
                itoa(num, buf, 16);
                Console::puts(buf);
            }
        } else {
            Console::putchar(*ptr);
        }
        ptr++;
    }
    va_end(args);

    Console::putchar('\n');
}

// Simple itoa for kernel logging
char* itoa(int value, char* str, int base) {
    char* ptr = str;
    char* low;

    if (base < 2 || base > 36) {
        *ptr = '\0';
        return str;
    }

    if (value < 0 && base == 10) {
        *ptr++ = '-';
        value = -value;
    }

    low = ptr;

    do {
        int rem = value % base;
        *ptr++ = (rem > 9) ? (rem - 10) + 'a' : rem + '0';
        value /= base;
    } while (value);

    *ptr-- = '\0';

    while (low < ptr) {
        char tmp = *low;
        *low++ = *ptr;
        *ptr-- = tmp;
    }

    return str;
}