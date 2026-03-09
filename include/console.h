#ifndef CONSOLE_H
#define CONSOLE_H

#include <cstdint>
#include <cstddef>

// VGA text mode constants
#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_BUFFER 0xB8000

enum class VGAColor {
    BLACK = 0,
    BLUE = 1,
    GREEN = 2,
    CYAN = 3,
    RED = 4,
    MAGENTA = 5,
    BROWN = 6,
    LIGHT_GREY = 7,
    DARK_GREY = 8,
    LIGHT_BLUE = 9,
    LIGHT_GREEN = 10,
    LIGHT_CYAN = 11,
    LIGHT_RED = 12,
    LIGHT_MAGENTA = 13,
    LIGHT_BROWN = 14,
    WHITE = 15,
};

// Console class for text output
class Console {
public:
    static void initialize();
    static void putchar(char c);
    static void puts(const char* str);
    static void printf(const char* format, ...);
    static void clear();
    static void set_color(VGAColor fg, VGAColor bg = VGAColor::BLACK);
    static void move_cursor(size_t x, size_t y);

private:
    static size_t cursor_x;
    static size_t cursor_y;
    static VGAColor current_fg;
    static VGAColor current_bg;
    static uint16_t* buffer;

    static uint16_t make_vga_entry(char c, VGAColor fg, VGAColor bg);
    static void scroll();
    static void update_cursor();
};

#endif // CONSOLE_H