/* NeuralOS Linker Script for x86_64 */

ENTRY(_start)

SECTIONS {
    . = 0x100000; /* Load at 1MB (lower memory) */

    __text_start = .;
    .text ALIGN(4K) : {
        *(.multiboot)
        *(.text*)
    }
    __text_end = .;

    .rodata ALIGN(4K) : {
        __rodata_start = .;
        *(.rodata*)
        __rodata_end = .;
    }

    .data ALIGN(4K) : {
        __data_start = .;
        *(.data*)
        __data_end = .;
    }

    .bss ALIGN(4K) : {
        __bss_start = .;
        *(COMMON)
        *(.bss*)
        __bss_end = .;
    }
    
    /* Calculate BSS size for clearing */
    _bss_size = __bss_end - __bss_start;

    /* Kernel heap will be allocated at runtime */
    __heap_start = .;
    
    /DISCARD/ : {
        *(.eh_frame)
        *(.note.GNU-stack)
    }
}
