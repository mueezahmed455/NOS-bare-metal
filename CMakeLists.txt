cmake_minimum_required(VERSION 3.16)
project(NeuralOS VERSION 0.1.0 LANGUAGES CXX)

# Set cross-compiler
set(CMAKE_CXX_COMPILER x86_64-linux-gnu-gcc)
set(CMAKE_C_COMPILER x86_64-linux-gnu-gcc)
set(CMAKE_ASM_COMPILER nasm)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Global freestanding flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ffreestanding -fno-exceptions -fno-rtti -nostdlib")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ffreestanding -nostdlib")

# Architecture detection
if(NOT ARCH)
    set(ARCH x86_64)
endif()

# Architecture-specific settings
if(ARCH STREQUAL "x86_64")
    set(ASM_SOURCES
        arch/x86_64/boot.asm
        arch/x86_64/interrupts.asm
    )
    set(ARCH_SOURCES
        arch/x86_64/arch.cpp
        arch/x86_64/gdt.cpp
        arch/x86_64/idt.cpp
        arch/x86_64/paging.cpp
    )
    set(LINKER_SCRIPT ${CMAKE_SOURCE_DIR}/arch/x86_64/linker.ld)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -m64 -mcmodel=kernel -mno-red-zone -ffreestanding -nostdlib -fno-pic")
    set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -f elf64")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -nostdlib")
endif()

# Kernel sources
set(KERNEL_SOURCES
    kernel/main.cpp
    kernel/kernel.cpp
    kernel/console.cpp
    kernel/memory.cpp
    kernel/scheduler.cpp
    kernel/syscalls.cpp
    kernel/filesystem.cpp
    kernel/network.cpp
    kernel/neural_core.cpp
    kernel/federated.cpp
    kernel/consensus.cpp
    kernel/shell_simple.cpp
    kernel/services.cpp
    ${ARCH_SOURCES}
)

# Compile assembly files with NASM
foreach(ASM_FILE ${ASM_SOURCES})
    get_filename_component(ASM_NAME ${ASM_FILE} NAME_WE)
    set(ASM_OBJ ${CMAKE_BINARY_DIR}/${ASM_NAME}.o)
    add_custom_command(
        OUTPUT ${ASM_OBJ}
        COMMAND ${CMAKE_ASM_COMPILER} -f elf64 -o ${ASM_OBJ} ${CMAKE_SOURCE_DIR}/${ASM_FILE}
        DEPENDS ${ASM_FILE}
        COMMENT "Assembling ${ASM_FILE}"
    )
    list(APPEND ASM_OBJS ${ASM_OBJ})
endforeach()

# Create kernel executable
add_executable(kernel ${KERNEL_SOURCES} ${ASM_OBJS})
target_include_directories(kernel PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/arch/${ARCH}
)

# Linker settings
if(LINKER_SCRIPT)
    set_target_properties(kernel PROPERTIES
        LINK_DEPENDS ${LINKER_SCRIPT}
        LINK_FLAGS "-T${LINKER_SCRIPT} -nostdlib -static"
    )
endif()

# Custom targets
add_custom_target(iso
    COMMAND mkdir -p ${CMAKE_BINARY_DIR}/iso/boot/grub
    COMMAND cp ${CMAKE_BINARY_DIR}/kernel ${CMAKE_BINARY_DIR}/iso/boot/
    COMMAND echo "menuentry \"NeuralOS\" { multiboot /boot/kernel }" > ${CMAKE_BINARY_DIR}/iso/boot/grub/grub.cfg
    COMMAND grub-mkrescue -o ${CMAKE_BINARY_DIR}/neuralos.iso ${CMAKE_BINARY_DIR}/iso
    DEPENDS kernel
    COMMENT "Creating bootable ISO"
)

add_custom_target(run
    COMMAND qemu-system-x86_64 -kernel ${CMAKE_BINARY_DIR}/kernel -serial stdio
    DEPENDS kernel
    COMMENT "Running NeuralOS in QEMU"
)

add_custom_target(debug
    COMMAND qemu-system-x86_64 -kernel ${CMAKE_BINARY_DIR}/kernel -s -S -serial stdio
    DEPENDS kernel
    COMMENT "Running NeuralOS in QEMU with GDB debugging"
)