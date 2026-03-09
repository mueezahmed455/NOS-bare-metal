#include "console.h"
#include "arch.h"

int Console::cursor_x = 0;
int Console::cursor_y = 0;
u8 Console::color = (VGA_LIGHT_GREY << 4) | VGA_BLACK;
u16* Console::buffer = (u16*)VGA_MEMORY;

void Console::initialize() {
    cursor_x = 0;
    cursor_y = 0;
    color = (VGA_LIGHT_GREY << 4) | VGA_BLACK;
    buffer = (u16*)VGA_MEMORY;
    clear();
}

void Console::clear() {
    for (int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        buffer[i] = (color << 8) | ' ';
    }
    cursor_x = 0;
    cursor_y = 0;
    updateCursor();
}

void Console::scroll() {
    // Move all lines up by one
    for (int i = 0; i < (VGA_HEIGHT - 1) * VGA_WIDTH; i++) {
        buffer[i] = buffer[i + VGA_WIDTH];
    }
    // Clear the last line
    for (int i = (VGA_HEIGHT - 1) * VGA_WIDTH; i < VGA_HEIGHT * VGA_WIDTH; i++) {
        buffer[i] = (color << 8) | ' ';
    }
    cursor_y = VGA_HEIGHT - 1;
}

void Console::putChar(char c) {
    if (c == '\n') {
        cursor_x = 0;
        cursor_y++;
    } else if (c == '\r') {
        cursor_x = 0;
    } else if (c == '\t') {
        cursor_x = (cursor_x + 8) & ~7;
    } else if (c == '\b') {
        if (cursor_x > 0) {
            cursor_x--;
            buffer[cursor_y * VGA_WIDTH + cursor_x] = (color << 8) | ' ';
        }
    } else {
        buffer[cursor_y * VGA_WIDTH + cursor_x] = (color << 8) | c;
        cursor_x++;
    }

    if (cursor_x >= VGA_WIDTH) {
        cursor_x = 0;
        cursor_y++;
    }

    if (cursor_y >= VGA_HEIGHT) {
        scroll();
    }

    updateCursor();
}

void Console::print(const char* str) {
    while (*str) {
        putChar(*str);
        str++;
    }
}

void Console::printHex(u64 value) {
    char hex_chars[] = "0123456789ABCDEF";
    char buffer[19];
    buffer[0] = '0';
    buffer[1] = 'x';
    
    for (int i = 0; i < 16; i++) {
        buffer[2 + i] = hex_chars[(value >> (60 - i * 4)) & 0xF];
    }
    buffer[18] = '\0';
    
    // Skip leading zeros
    int start = 2;
    while (start < 17 && buffer[start] == '0') {
        start++;
    }
    if (start == 18) start = 17; // Print at least one zero
    
    print(&buffer[start]);
}

void Console::printDec(i64 value) {
    if (value < 0) {
        putChar('-');
        value = -value;
    }
    
    char buffer[22];
    int i = 0;
    
    do {
        buffer[i++] = '0' + (value % 10);
        value /= 10;
    } while (value > 0);
    
    // Print in reverse
    while (i > 0) {
        putChar(buffer[--i]);
    }
}

void Console::setCursor(int x, int y) {
    cursor_x = x;
    cursor_y = y;
    updateCursor();
}

void Console::setColor(u8 fg, u8 bg) {
    color = (bg << 4) | fg;
}

void Console::updateCursor() {
    u16 pos = cursor_y * VGA_WIDTH + cursor_x;
    Arch::outb(0x3D4, 0x0F);
    Arch::outb(0x3D5, (u8)(pos & 0xFF));
    Arch::outb(0x3D4, 0x0E);
    Arch::outb(0x3D5, (u8)((pos >> 8) & 0xFF));
}
