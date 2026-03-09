#ifndef KERNEL_H
#define KERNEL_H

#include <cstdint>
#include <cstddef>

// Kernel version
#define KERNEL_VERSION "0.1.0"
#define KERNEL_NAME "NeuralOS"

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
using isize = ptrdiff_t;

// Kernel entry point
extern "C" void kernel_main();

// Kernel panic
[[noreturn]] void panic(const char* message);

// Memory operations
void* kmalloc(size_t size);
void kfree(void* ptr);
void* krealloc(void* ptr, size_t size);

// String utilities
size_t strlen(const char* str);
char* strcpy(char* dest, const char* src);
int strcmp(const char* a, const char* b);
void* memset(void* dest, int value, size_t count);
void* memcpy(void* dest, const void* src, size_t count);
char* itoa(int value, char* str, int base);

// Kernel logging
enum class LogLevel {
    DEBUG,
    INFO,
    WARN,
    ERROR
};

void klog(LogLevel level, const char* format, ...);

#endif // KERNEL_H