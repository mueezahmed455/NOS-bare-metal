#ifndef CONSOLE_H
#define CONSOLE_H

#include "kernel.h"

// VGA Text mode constants
#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

// VGA colors
enum VGAColor {
    VGA_BLACK = 0,
    VGA_BLUE = 1,
    VGA_GREEN = 2,
    VGA_CYAN = 3,
    VGA_RED = 4,
    VGA_MAGENTA = 5,
    VGA_BROWN = 6,
    VGA_LIGHT_GREY = 7,
    VGA_DARK_GREY = 8,
    VGA_LIGHT_BLUE = 9,
    VGA_LIGHT_GREEN = 10,
    VGA_LIGHT_CYAN = 11,
    VGA_LIGHT_RED = 12,
    VGA_LIGHT_MAGENTA = 13,
    VGA_YELLOW = 14,
    VGA_WHITE = 15,
};

// Console class for VGA text output
class Console {
public:
    static void initialize();
    static void clear();
    static void putChar(char c);
    static void print(const char* str);
    static void printHex(u64 value);
    static void printDec(i64 value);
    static void setCursor(int x, int y);
    static void setColor(u8 fg, u8 bg);

private:
    static int cursor_x;
    static int cursor_y;
    static u8 color;
    static u16* buffer;

    static void scroll();
    static void updateCursor();
};

#endif // CONSOLE_H
