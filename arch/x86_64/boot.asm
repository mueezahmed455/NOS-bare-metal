; NeuralOS Bootloader
; x86_64 Multiboot2 compliant

section .multiboot
align 8

; Multiboot2 header
multiboot_header:
    dd 0xE85250D6                  ; Magic number (Multiboot2)
    dd 0                           ; Protected mode
    dd header_end - multiboot_header ; Header length
    dd 0x100000000 - (0xE85250D6 + 0 + (header_end - multiboot_header)) ; Checksum

; Required tag
    dw 0                           ; Type (required)
    dw 0                           ; Flags
    dd tag_required_end - tag_required ; Size
tag_required:
    dd 0                           ; Architecture (0 = i386, 1 = x86_64)
    dw 0, 0                        ; Padding
tag_required_end:

; End tag
    dw 0                           ; Type (end)
    dw 0                           ; Flags
    dd 8                           ; Size
header_end:

section .bss
align 16
stack_bottom:
    resb 65536                     ; 64 KB stack
stack_top:

section .text
global _start
extern kernel_main

_start:
    ; Check if we were booted with Multiboot2
    cmp eax, 0x36D76289
    jne .no_multiboot

    ; Save multiboot info pointer
    mov [multiboot_ptr], ebx

    ; Set up stack
    mov rsp, stack_top

    ; Call kernel main
    call kernel_main

    ; Should not return
    cli
.hang:
    hlt
    jmp .hang

.no_multiboot:
    ; Not booted with Multiboot2
    cli
.hang2:
    hlt
    jmp .hang2

; Data section for storing multiboot pointer
section .data
multiboot_ptr:
    dq 0
