#include "console.h"
#include "kernel.h"
#include "arch.h"
#include <cstdarg>

// Static member initialization
size_t Console::cursor_x = 0;
size_t Console::cursor_y = 0;
VGAColor Console::current_fg = VGAColor::WHITE;
VGAColor Console::current_bg = VGAColor::BLACK;
uint16_t* Console::buffer = reinterpret_cast<uint16_t*>(VGA_BUFFER);

void Console::initialize() {
    clear();
    set_color(VGAColor::WHITE, VGAColor::BLACK);
}

void Console::putchar(char c) {
    if (c == '\n') {
        cursor_x = 0;
        cursor_y++;
    } else if (c == '\t') {
        cursor_x = (cursor_x + 4) & ~(4 - 1);
    } else if (c == '\r') {
        cursor_x = 0;
    } else {
        buffer[cursor_y * VGA_WIDTH + cursor_x] = make_vga_entry(c, current_fg, current_bg);
        cursor_x++;
    }

    if (cursor_x >= VGA_WIDTH) {
        cursor_x = 0;
        cursor_y++;
    }

    scroll();
    update_cursor();
}

void Console::puts(const char* str) {
    while (*str) {
        putchar(*str++);
    }
}

void Console::printf(const char* format, ...) {
    va_list args;
    va_start(args, format);

    const char* ptr = format;
    while (*ptr) {
        if (*ptr == '%') {
            ptr++;
            if (*ptr == 's') {
                const char* str = va_arg(args, const char*);
                puts(str);
            } else if (*ptr == 'd') {
                int num = va_arg(args, int);
                char buf[32];
                itoa(num, buf, 10);
                puts(buf);
            } else if (*ptr == 'x') {
                unsigned int num = va_arg(args, unsigned int);
                char buf[32];
                itoa(num, buf, 16);
                puts(buf);
            } else if (*ptr == 'c') {
                char c = static_cast<char>(va_arg(args, int));
                putchar(c);
            }
        } else {
            putchar(*ptr);
        }
        ptr++;
    }

    va_end(args);
}

void Console::clear() {
    for (size_t y = 0; y < VGA_HEIGHT; y++) {
        for (size_t x = 0; x < VGA_WIDTH; x++) {
            buffer[y * VGA_WIDTH + x] = make_vga_entry(' ', current_fg, current_bg);
        }
    }
    cursor_x = 0;
    cursor_y = 0;
    update_cursor();
}

void Console::set_color(VGAColor fg, VGAColor bg) {
    current_fg = fg;
    current_bg = bg;
}

void Console::move_cursor(size_t x, size_t y) {
    cursor_x = x;
    cursor_y = y;
    update_cursor();
}

uint16_t Console::make_vga_entry(char c, VGAColor fg, VGAColor bg) {
    return static_cast<uint16_t>(c) | (static_cast<uint16_t>(fg) << 8) | (static_cast<uint16_t>(bg) << 12);
}

void Console::scroll() {
    if (cursor_y >= VGA_HEIGHT) {
        // Move all lines up
        for (size_t y = 1; y < VGA_HEIGHT; y++) {
            for (size_t x = 0; x < VGA_WIDTH; x++) {
                buffer[(y - 1) * VGA_WIDTH + x] = buffer[y * VGA_WIDTH + x];
            }
        }

        // Clear the last line
        for (size_t x = 0; x < VGA_WIDTH; x++) {
            buffer[(VGA_HEIGHT - 1) * VGA_WIDTH + x] = make_vga_entry(' ', current_fg, current_bg);
        }

        cursor_y = VGA_HEIGHT - 1;
    }
}

void Console::update_cursor() {
    uint16_t position = cursor_y * VGA_WIDTH + cursor_x;

    // Send position to VGA controller
    Arch::outb(0x3D4, 0x0F);
    Arch::outb(0x3D5, static_cast<uint8_t>(position & 0xFF));
    Arch::outb(0x3D4, 0x0E);
    Arch::outb(0x3D5, static_cast<uint8_t>((position >> 8) & 0xFF));
}